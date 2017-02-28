import datetime

from django.db import models
from restless.models import serialize

class TimestampedMixin(models.Model):
    """
    Handy mixin for adding created and modified dates to models.

    """
    created     = models.DateTimeField(auto_now_add=True)
    modified    = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        super(TimestampedMixin, self).save(*args, **kwargs)


class JSONSerializable(object):
    def to_json(self, *args, **kwargs):
        return serialize(self, *args, **kwargs)