import logging
import requests

from c2 import settings

logger = logging.getLogger("console")

def perform_request(url, params={}):
    r = requests.get(url, params=params)
    try:
        data = r.json()
    except Exception as e:
        logger.error("Error retrieving information from: %s" % url)
        data = None

    return data


# TODO: Add a cacheing layer to these requests
class EventAPI(object):
    """
    High level wrapper for interacting with the Skyhook Event Service.

    """
    def __init__(self):
        self.api = settings.SKYHOOK_HOST

    def get_event(self, event_id):
        """
        Retreives an individual event
        """
        url = "%s/api/events/%s" % (self.api, event_id, )
        return perform_request(url)

    def get_events(self, event_ids):
        """
        Retrieve a list of events with given uuids

        """
        if not event_ids:
            return None

        url = "%s/api/events" % (self.api, )
        params = { "event_ids": ",".join(event_ids) }

        data = perform_request(url, params=params)

        if data:
            data = data.get("events", [])

        return data

    # TODO: Handle paginated requests/responses
    def events_for_team(self, team_id):
        """
        Retrieve events for a team

        """
        url = "%s/api/teams/%s" % (self.api, team_id, )
        data = perform_request(url)

        if data:
            return data.get("events", [])
        return data

    # TODO: Handle paginated requests/responses
    def events_for_sensor(self, team_id, sensor_id):
        """
        Retrieve events for a sensor

        """

        url = "%s/api/teams/%s/sensors/%s" % (self.api, team_id, sensor_id, )
        data = perform_request(url)

        if data:
            return data.get("events", [])

        return data
