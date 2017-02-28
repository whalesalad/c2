import json
import socket
# import multiprocessing

from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings

from c2.sensors.models import Sensor, Cluster
from c2.rules.tasks import create_advisory_from_event_payload

from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer #, MultiProcessConsumer
from kafka.common import OffsetOutOfRangeError

kafka_client = KafkaClient(settings.KAFKA_HOST)

ADVISORY_EVENTS = (
    "anomalous_process_behavior",
    "unexpected_child_process",
    "anomalous_package",
    "malicious_file",
)

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--beginning",
            action="store_true",
            dest="beginning",
            default=False,
            help="Start from the beginning of the topic (seek to 0)"),

        make_option("--end",
            action="store_true",
            dest="end",
            default=False,
            help="Start from the end of the topic (seek to 0)"),

        make_option("--dev",
            action="store_true",
            dest="dev",
            default=False,
            help="Start a few hundred back from the end of the topic to warm local events."),
    )

    topic = settings.KAFKA_EVENT_TOPIC

    @property
    def consumer_name(self):
        basename = str(__name__).split(".")[-1].replace("_", "-")
        return "%s-%s" % (basename, socket.gethostname(), )

    def handle(self, *args, **options):
        self.stdout.write("Starting %s worker for %s." % (self.topic, self.consumer_name, ))

        self.consumer = SimpleConsumer(client=kafka_client,
                                       group=self.consumer_name,
                                       topic=self.topic,
                                       max_buffer_size=1024*1024*2)

        # self.consumer = MultiProcessConsumer(client=kafka_client,
        #                                      group=self.consumer_name,
        #                                      topic=self.topic,
        #                                      num_procs=multiprocessing.cpu_count())

        self.dev_mode = False
        if options["beginning"]:
            self.consumer.seek(0, 0)
        elif options["end"]:
            self.consumer.seek(0, 2)
        elif options["dev"]:
            self.dev_mode = True
            self.consumer.seek(-300, 2)

        try:
            while bool(self.consumer):
                try:
                    for m in self.consumer:
                        self.handle_message(m)
                except OffsetOutOfRangeError:
                    self.stderr.write("Offset out of range error.  Seeking to beginning.")
                    self.consumer.seek(0, 0)

        except KeyboardInterrupt:
            self.consumer = False

            kafka_client.close()

            self.stdout.write("Shutting down %s worker." % (self.topic, ))
            self.stdout.write("Got Ctrl-C, terminating %s consumer." % (self.topic, ))

    def handle_message(self, message_and_offset):
        offset = message_and_offset.offset
        message = message_and_offset.message
        payload = json.loads(message.value)

        team = payload.get("team")
        event_type = payload.get("event")

        if not payload.get("event_id"):
            self.stdout.write("Skipping event with no UUID <Offset: %s>" % offset)
            return

        # Process Advisories
        if event_type in ADVISORY_EVENTS:
            task = create_advisory_from_event_payload
            if self.dev_mode:
                advisory = task(payload)
                if advisory:
                    print "Created %s" % advisory
            else:
                task.apply_async(args=(payload, ))

        # New Sensor Enrollment
        if event_type == "sensor_new":
            return Sensor.create_from_payload(payload)

        # Cluster Destroy Event
        if event_type == "dead_packages_group":
            cluster_id = payload["value"].values()[0]
            try:
                return Cluster.objects.get(uuid=cluster_id).delete()
            except Cluster.DoesNotExist:
                return
