import pprint
import datetime
import itertools

from restless.models import serialize

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import get_resolver
from django.db.models import Count, Q
from django.template.response import TemplateResponse

from c2.accounts.models import Team
from c2.sensors.models import Sensor
from c2.advisories.models import Advisory
from c2.rules.models import Rule
from c2.snapshot.presenters import SnapshotPresenter
from c2.services import RelatedEventsService

EXCLUDE_KEYS = ('connections', 'memory', 'loadavg', 'sock_stats', 'interface_stats', 'arp', 'uptime', )

@staff_member_required
def index(request, template='playground/index.html'):
    events_total = Event.objects.count()

    event_key_stats = []
    for e in Event.objects.values("key").annotate(Count("key")).order_by():
        event_key_stats.append({
            'key': e['key'],
            'count': e['key__count'],
            'percent': (e['key__count'] / float(events_total) * 100)
        })

    class_map = {
        'added': 'progress-bar-success',
        'changed': 'progress-bar-warning',
        'removed': 'progress-bar-danger'
    }

    event_type_stats = []
    for e in Event.objects.values("event").annotate(Count("event")).order_by():
        event_type_stats.append({
            'css_class': class_map[e['event']],
            'event': e['event'],
            'count': e['event__count'],
            'percent': (e['event__count'] / float(events_total) * 100)
        })

    return TemplateResponse(request, template, context={
        'events_total': events_total,
        'event_key_stats': event_key_stats,
        'event_type_stats': event_type_stats
    })

@staff_member_required
def advisory_delay(request, template='playground/advisory_delay.html'):
    advisories = Advisory.objects.all().exclude(rule='fresh_sensor')[:100]

    return TemplateResponse(request, template, context={
        'advisories': advisories
    })

@staff_member_required
def advisory_list(request, template='playground/advisory_list.html'):
    rule = request.GET.get('rule', None)

    if rule:
        advisories = Advisory.objects.filter(rule__slug=rule)
    else:
        advisories = Advisory.objects.all()

    rules = Rule.objects.all().annotate(num_advisories=Count("advisories")).order_by()

    return TemplateResponse(request, template, context={
        'advisories': advisories[:100],
        'rules': rules,
    })

@staff_member_required
def advisory_detail(request, advisory_id, template='playground/advisory_detail.html'):
    advisory = Advisory.objects.get(id=advisory_id)

    svc = RelatedEventsService(advisory.event)

    return TemplateResponse(request, template, context={
        'advisory': advisory,
        'events': svc.all(),
        'primary': advisory.event
    })


@staff_member_required
def aws_info(request, identifier=None, template='playground/aws_info.html'):
    """

    """

    instances = []
    groups = {}

    keys = AmazonKey.objects.prefetch_related('team').all()
    teams = list(set([key.team for key in keys]))

    if identifier:
        team = Team.objects.get(identifier=identifier)
        key = keys.get(team=team)
        svc = key.get_svc(regions=('us-west-1', 'us-west-2', 'us-east-1', ), cache_timeout=600)

        instances = svc.instances
        groups = svc.groups

    else:
        key = None
        team = None

    return TemplateResponse(request, template, context={
        'key': key or None,
        'team': team,
        'teams': teams,
        'instances': instances,
        'groups': groups
    })

@staff_member_required
def snapshot_list(request, template=None):
    sensors = Sensor.objects.prefetch_related('team').all().order_by('name')

    return TemplateResponse(request, template, context={
        'sensors': sensors,
    })

@staff_member_required
def snapshot_detail(request, identifier=None, uuid=None, key=None, template=None):
    attribute = None
    sensor = Sensor.objects.get(uuid=uuid, team__identifier=identifier)
    snapshot = sensor.snapshot

    if key:
        attribute = getattr(snapshot, key, {})

    return TemplateResponse(request, template, context={
        'sensor': sensor,
        'snapshot': snapshot,
        'key': key,
        'attribute': attribute
    })

@staff_member_required
def event_list(request, key_filter=None, template=None):
    uuid = request.GET.get('uuid', None)

    if uuid:
        events = Event.objects\
            .filter(sensor__uuid=uuid, event='changed')\
            .order_by('-occurred')\
            .exclude(key__in=EXCLUDE_KEYS)[:200]

        # events = itertools.ifilterfalse(lambda x: x.key == 'processes' and x.event == 'changed', events)

    else:
        events = []

        keys = Event.objects.order_by().values_list("key", flat=True).distinct()

        if key_filter:
            keys = (key_filter, )
        else:
            keys = set(keys) - set(EXCLUDE_KEYS)

        for k in keys:
            events.extend(Event.objects.filter(key=k, event='changed', )[:5])

    return TemplateResponse(request, template, context={
        'events': events,
    })