from c2.api.presenter import BasePresenter
from c2.events.presenters import EventPresenter


class AdvisoryPresenter(BasePresenter):
    @property
    def serialized(self):
        return self.serialize(self.objects, fields=[
            "uuid",
            "title",
            "created",
            ("sensor_groups", lambda a: a.sensor.groups or []),
            ("sensor_names", lambda a: [a.sensor.name or a.sensor.uuid]),
            ("sensor_uuids", lambda a: [a.sensor.uuid]),
            ("rule", lambda a: a.rule.slug),
        ])


class AdvisoryDetailPresenter(BasePresenter):
    @property
    def serialized(self):
        return self.serialize(self.objects, fields=[
            ("details", lambda a: a.details),
            ("events", lambda a: EventPresenter(a.events).serialized(a.sensors)),
        ])

class NotificationPresenter(BasePresenter):
    @property
    def serialized(self):
        return self.serialize(self.objects, fields=[
            "id",
            ("sensor", lambda n: self.serialize(n.advisory.sensor_id)),
        ])