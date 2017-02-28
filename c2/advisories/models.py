from django.db import models
from django.core.cache import get_cache

from django_extensions.db.fields import UUIDField
from django_extensions.db.fields.json import JSONField

from c2.sensors.models import Sensor
from c2.rules.models import Rule
from c2.accounts.models import User, Team

from c2.utils.models.mixins import TimestampedMixin

from c2.events import EventAPI
from c2.advisories.graph_query import GraphQuery

cache = get_cache('event_cache')

class Advisory(TimestampedMixin, models.Model):
    """
    Object to store advisories.

    """
    title  = models.TextField(u"Title")
    uuid   = UUIDField(u"UUID", primary_key=True)
    rule   = models.ForeignKey(Rule, related_name="advisories")
    team   = models.ForeignKey(Team, related_name="advisories")
    sensor = models.ForeignKey(Sensor, related_name="advisories")

    class Meta:
        ordering = ("-created", )
        get_latest_by = "created"
        verbose_name_plural = u"advisories"

    def __unicode__(self):
        return u"%s Advisory" % (self.rule, )

    def __repr__(self):
        return u"%s Advisory" % (self.rule, )

    @property
    def _events(self):
        return cache.get("%s.events" % self.uuid)

    @property
    def _details(self):
        return cache.get("%s.details" % self.uuid)

    @property
    def events(self):
        cached = self._events
        if cached:
            return cached

        event_ids = GraphQuery().get_related_events(self.uuid)

        if not event_ids:
            event_ids = []

        if self.uuid not in event_ids:
            event_ids.append(self.uuid)

        events = EventAPI().get_events(event_ids)

        cache.set("%s.events" % self.uuid, events, 30)
        return events

    @property
    def sensors(self):
        try:
            sensor_ids = [e["sensor"] for e in self.events]
            return Sensor.objects.filter(uuid__in=sensor_ids)
        except:
            return []

    @property
    def groups(self):
        groups = []
        for s in self.sensors:
            groups.append(s.groups)

        groups = list(set(groups))
        return groups

    @property
    def details(self):
        cached = self._details
        if cached:
            return cached

        details = EventAPI().get_event(self.uuid).get("value")
        cache.set("%s.details" % self.uuid, details, 60)

        return details


class Notification(TimestampedMixin, models.Model):
    """
    Object representing a read/unread notification for each user.

    """
    advisory = models.ForeignKey(Advisory)
    user     = models.ForeignKey(User, related_name="notifications", db_index=True)
    unread   = models.BooleanField(default=True)