from logging import getLogger
from django.core.management.base import BaseCommand, CommandError
from c2.snapshot import SnapshotAPI

from c2 import settings
from c2.accounts.models import Team
from c2.sensors.models import Sensor

logger = getLogger(__name__)

class Command(BaseCommand):
    help = "Drops all sensors (example team) and pre-loads them from snapshot."

    def handle(self, *args, **options):
        identifier = 'example'
        if args:
            identifier = args[0]

        try:
            team = Team.objects.get(identifier=identifier)
        except Team.DoesNotExist:
            raise CommandError("Team %s does not exist." % identifier)

        # Delete all current sensors
        team.sensors.all().delete()

        uuids = SnapshotAPI(identifier).sensors

        for uuid in uuids:
            Sensor.objects.create(uuid=uuid, team=team)
