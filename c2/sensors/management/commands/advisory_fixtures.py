import os
from django.conf import settings

from c2.sensors.management.base_kafka_worker import BaseKafkaWorker

class Command(BaseKafkaWorker):
    """
    Pulls lots of messages off the advisory queue and makes fixtures out of them
    so that tests can be performed on those fixtures.

    """

    @property
    def topic(self):
        return 'advisories'

    @property
    def consumer_name(self):
        return 'advisory_fixture_worker'

    def before_start(self):
        if self.consumer:
            self.consumer.seek(offset=-500, whence=2)

        base_path = os.path.join(settings.BASE_DIR, 'fixtures')
        destination_path = '%s/advisory_messages.json' % base_path
        os.remove(destination_path)
        self.destination = open(destination_path, 'w')

    def process_message(self, message):
        self.destination.write(message + '\n')

    def before_finish(self):
        self.destination.close()

