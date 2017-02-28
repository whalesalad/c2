import stat
import pprint
import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from c2.sensors.models import Advisory, Event

from c2.rules.tasks import create_advisories_from_event

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete existing advisories.'),

        make_option('--today',
            action='store_true',
            dest='today',
            default=False,
            help='Reprocess events for only today'),

        make_option('--key',
            action='store',
            type='string',
            dest='key',
            help='Limit rule processing to a single key.')
    )

    def handle(self, *args, **options):
        if options['delete']:
            Advisory.objects.all().delete()

        events = Event.objects.all()

        if options['today']:
            events = events.filter(occurred__gte=datetime.datetime.now() - datetime.timedelta(days=1))

        if options['key']:
            events = events.filter(key=options['key'])

        num_events = events.count()

        self.stdout.write("Reprocessing %s event(s) for advisories." % num_events)

        for event_id in events.values_list('id', flat=True):
            create_advisories_from_event(event_id)

        self.stdout.write("Finished queueing up tasks.")
