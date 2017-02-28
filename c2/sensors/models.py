import re
import arrow
import json
import pprint

from jinja2 import Environment

from django.db import models
from django.utils import timezone
from django.core.cache import get_cache

from django_extensions.db.fields import UUIDField
from django_extensions.db.fields.json import JSONField

from djorm_pgarray.fields import TextArrayField

from dictdiffer import diff

from c2 import settings
from c2.api.utils import epoch
from c2.accounts.models import Team
from c2.snapshot import SnapshotAPI

from c2.sensors.utils import generate_cluster_name
from c2.sensors.tasks import sync_sensor_hostname, sync_sensor_cloud_key
from c2.utils.models.mixins import TimestampedMixin, JSONSerializable

jinja_env = Environment()

cache = get_cache('default')


class Cluster(JSONSerializable, models.Model):
    uuid    = UUIDField(u'UUID', primary_key=True)
    name    = models.CharField(u'Name', max_length=250, default=generate_cluster_name)
    is_user = models.BooleanField(default=False)

    team    = models.ForeignKey(Team, related_name='clusters')

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return "%s : %s" % (self.uuid, self.name, )

    def __repr__(self):
        return 'Cluster %s' % self.name


class Sensor(JSONSerializable, TimestampedMixin, models.Model):
    uuid        = UUIDField(u'UUID', primary_key=True)
    name        = models.CharField(u'Name', max_length=250, null=True, blank=True)
    team        = models.ForeignKey(Team, related_name='sensors')

    groups      = TextArrayField(null=True, blank=True)
    active      = models.BooleanField(u'Active', default=True, blank=False, null=False)

    cloud_key   = models.CharField(u'Cloud Key', max_length=250, null=True, blank=True)

    class Meta:
        ordering = ('-created', )
        get_latest_by = 'created'

    def __unicode__(self):
        return self.name or self.uuid

    @classmethod
    def create_from_payload(self, payload):
        """
        Creates a new Sensor object from a JSON payload
        (reads off kafka queue for `sensor_new` events)
        """
        try:
            team = Team.objects.get(identifier=payload.get('team'))
        except Team.DoesNotExist:
            return None

        # Find or create the sensor
        sensor, created = Sensor.objects.get_or_create(uuid=payload['sensor'], team=team)
        return sensor

    @property
    def _snapshot(self):
        return cache.get('%s_snapshot' % self.uuid)

    @property
    def snapshot(self):
        if self._snapshot:
            return self._snapshot

        snapshot = SnapshotAPI(self.team.identifier).sensor_state(self.uuid)

        # Prevent rapid fire of snapshot updates
        cache.set('%s_snapshot' % self.uuid, snapshot, 5)
        return snapshot

    @property
    def group(self):
        if self.groups:
            return self.groups[0]
        else:
            return None

    @group.setter
    def group(self, group):
        self.groups = [group]

    def set_properties_from_snapshot(self):
        self.cloud_key = self.get_cloud_key()
        self.name = self.get_hostname()

    def get_name(self):
        if not self.name:
            sync_sensor_hostname.apply_async(args=(self, ))

        return self.name

    def get_key(self):
        if not self.cloud_key:
            sync_sensor_cloud_key.apply_async(args=(self, ))

        return self.cloud_key

    @property
    def cloud_metadata(self):
        return self.snapshot.get('cloud_metadata')

    def get_hostname(self):
        # Hierarchy for sensor naming
        # AWS (Name) Tag -> Collector Hostname -> Sensor UUID
        name = None

        name = self.cloud_metadata.get('tags', {}).get('Name')

        if not name:
            name = self.snapshot.get('hostname', {}).get('hostname')

        return name

    def get_cloud_key(self):
        metadata = self.cloud_metadata

        if not metadata:
            return None

        return "%s.%s.%s" % (metadata.get('provider') or metadata['type'], # Handle deprecated messages
                             metadata['availability_zone'],
                             metadata['instance_id'], )
