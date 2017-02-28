import json

from restless.models import serialize

from c2.api.utils import epoch


class BasePresenter():
    def __init__(self, objects):
        self.objects = objects

    def epoch(self, val):
        return epoch(val)

    @property
    def to_json(self):
        return json.dumps(self.serialized)

    def serialize(self, *args, **kwargs):
        return serialize(*args, **kwargs)

    @property
    def serialized(self):
        return self.serialize(self.objects, fields=self.fields)
