import logging
import requests

from c2 import settings

logger = logging.getLogger('c2.snapshot')

"""
Timestamp should be stored as a datetime object.

urns = [
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
]

"""
def perform_request(url):
    r = requests.get(url)
    try:
        return r.json()
    except Exception as e:
        logger.error('Error retrieving snapshot data from Snapshot for: %s' % url)
        return None

class SnapshotAPI(object):
    """
    API interactions with the Snapshot Service

    """
    def __init__(self, identifier):
        self.identifier = identifier
        self.url = settings.VERMONT_HOST

    @property
    def state(self):
        url = "%s/state/teams/%s" % (self.url, self.identifier, )
        return perform_request(url)

    @property
    def sensors(self):
        """
        List of all sensors that have had activity collected

        """
        url = "%s/state/teams/%s/sensors" % (self.url, self.identifier, )
        data = perform_request(url)
        return data.get('sensors', [])

    @property
    def clusters(self):
        url = "%s/state/teams/%s/clusters" % (self.url, self.identifier, )
        return perform_request(url)

    @property
    def cloud_information(self):
        """
        Asset list from the teams cloud providers

        """
        url = "%s/state/teams/%s/cloud" % (self.url, self.identifier, )
        return perform_request(url)

    def sensor_state(self, uuid):
        """
        Return current state attributes for sensor

        """
        url = "%s/state/teams/%s/sensors/%s" % (self.url, self.identifier, uuid)
        return perform_request(url)

    def sensor_process_tree(self, uuid):
        url = "%s/state/teams/%s/sensors/%s/process" % (self.url, self.identifier, uuid)
        return perform_request(url)
