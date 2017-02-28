import datetime
import pprint

from django.utils.timezone import utc

from c2.api.presenter import BasePresenter
from c2.advisories.presenters import AdvisoryPresenter
from c2.services import RelatedEventsService
from c2.utils.formatting import human_bytes, human_delta, event_delta

from c2.sensors.models import Cluster


class ClusterPresenter(BasePresenter):
    @property
    def serialized(self):
        return self.serialize(self.objects, fields=[
            'uuid',
            'name',
            'is_user',
            ('members', lambda c: c.members),
        ])


class SensorPresenter(BasePresenter):
    @property
    def serialized(self):
        return self.serialize(self.objects, fields=[
            'uuid',
            ('name', lambda s: s.get_name() or s.uuid),
            'created',
            ('cloud_key', lambda s: s.get_key()),
            ('state', lambda s: getattr(s, 'state', {})),
            ('groups', lambda s: s.groups or []),
        ])

class SensorDetailPresenter(BasePresenter):
    @property
    def serialized(self):
        return self.serialize(self.objects, fields=[
            ('name', lambda s: s.name or s.uuid),
            'created',
            ('cloud_key', lambda s: s.get_key()),
            ('state', lambda s: s.snapshot),
            ('groups', lambda s: s.groups or []),
        ])
