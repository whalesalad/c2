from django.utils.timezone import utc
from c2.api.presenter import BasePresenter
from restless.models import serialize


class SnapshotPresenter(BasePresenter):
    @property
    def serialized(self):
        return self.serialize(self, fields=[
            "processes",
            "memory",
            "disks",
            "users",
            "packages",
            "arp",
            "hostname",
            "filesystem",
            "sessions",
            "loadavg",
            "activity",
            "groups",
            "uname",
            "uptime",
            "cloud_metadata",
            "time",
            "distro"
        ])
