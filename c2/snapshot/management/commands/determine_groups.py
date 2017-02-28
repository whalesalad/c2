import re
import pprint
import json

from collections import Counter
from logging import getLogger

from django.core.management.base import BaseCommand, CommandError

from c2.accounts.models import Team
from c2.snapshot import SnapshotAPI

logger = getLogger(__name__)

api = SnapshotAPI()

def get_unique_ports(connections):
    ports = set()

    for conn in connections:
        if conn.get('status', None) == 'LISTEN':
            parts = conn['local'].split(':')
            ports.add(int(parts[-1]))

    return list(ports)

def guess_process_name(command):
    accumulator = Counter()
    parts = filter(None, re.split('/|--| |-', command))

    for p in parts:
        if len(p) > 2:
            accumulator[p] += 1

    common_command, count = accumulator.most_common()[0]

    return common_command

process_pattern = re.compile(r'^(?P<comm>[\w]+)\/')

def clean_process_name(name):
    if not name.startswith('/'):
        match = process_pattern.match(name)
        if match:
            return match.groups()[0].rstrip()

    return name

def get_unique_processes(processes):
    commands = set()

    for p in processes:

        if len(p['cmdline']):
            commands.add(guess_process_name(' '.join(p['cmdline'])))
        else:
            commands.add(clean_process_name(p['name']))

    return list(filter(None, commands))

def get_unique_users(users):
    users = set([ u['name'] for u in users ])
    return list(users)

class Command(BaseCommand):
    help = 'Drops all sensors (example team) and pre-loads them from Coyote snapshots'

    def handle(self, *args, **options):
        identifier = 'example'
        if args:
            identifier = args[0]

        try:
            team = Team.objects.get(identifier=identifier)
        except Team.DoesNotExist:
            raise CommandError('Team %s does not exist.' % identifier)

        snapshots = api.team(identifier).sensors

        sensors = {}

        for s in snapshots:
            sensor = {
                'hostname': s.hostname['value']['hostname'],
                'ports': get_unique_ports(s.connections['value']),
                'processes': get_unique_processes(s.processes['value']),
                'users': get_unique_users(s.users['value'])
            }

            sensors[s.uuid] = sensor

        print
        print json.dumps(sensors, sort_keys=True, indent=2, separators=(',', ': '))
        print


