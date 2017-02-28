import logging
from itertools import chain

from restless.models import serialize
from restless.http import Http403, Http404

from django.core.paginator import Paginator, EmptyPage

from c2 import settings
from c2.utils import safe_cast
from c2.api.utils import AuthenticatedEndpoint

from c2.snapshot import SnapshotAPI
from c2.events import EventAPI

from c2.sensors.models import Sensor, Cluster
from c2.sensors.forms import SensorForm, ClusterForm

from c2.events.presenters import EventPresenter
from c2.advisories.presenters import AdvisoryPresenter
from c2.snapshot.presenters import SnapshotPresenter
from c2.sensors.presenters import (SensorPresenter,
                                   ClusterPresenter,
                                   SensorDetailPresenter)

logger = logging.getLogger('console')


class CloudAssetList(AuthenticatedEndpoint):
    """
    List of all cloud assets (GET)

    """
    def get(self, request):
        team = request.user.team.identifier
        return SnapshotAPI(team).cloud_information


class SensorClusterList(AuthenticatedEndpoint):
    """
    Return a list of all clusters (GET)

    """
    def get(self, request):
        team = request.user.team
        clusters = SnapshotAPI(team.identifier).clusters

        results = []
        for uuid, members in clusters.iteritems():
            cluster, created = Cluster.objects.get_or_create(uuid=uuid, team=team)
            cluster.members = members
            results.append(cluster)

        return ClusterPresenter(results).serialized

    def post(self, request):
        try:
            cluster = Cluster.objects.get(pk=request.data['uuid'])
        except Cluster.DoesNotExist:
            return Http404("That cluster does not exist.")

        form = ClusterForm(request.data, instance=cluster)

        if form.is_valid():
            form.save()
        else:
            return serialize([(k, v[0]) for k, v in form.errors.items()])

        return serialize(cluster)


class SensorGroupList(AuthenticatedEndpoint):
    """
    Return a list of all groups (GET)

    """
    def get(self, request):
        groups = []

        for sensor in request.user.team.sensors.all():
            if sensor.group:
                for group in sensor.groups:
                    groups.append(str(group))
            else:
                groups.append('ungrouped')

        return serialize(set(groups))


class SensorList(AuthenticatedEndpoint):
    """
    List of sensor objects (GET)

    """
    def get(self, request):
        # currently returns all active sensors owned by the user's team
        # the user can have many teams, but initially they have one single team
        sensors = request.user.team.sensors \
                      .filter(active=True) \
                      .order_by('-created')

        team = request.user.team.identifier
        state = SnapshotAPI(team).state

        # Augment registered sensors with state information
        for sensor in sensors:
            sensor.state = state.get(sensor.uuid, {})

        return SensorPresenter(sensors).serialized


class Detail(object):
    def get_sensor(self, request, sensor_id):
        try:
            sensor = Sensor.objects.get(uuid=sensor_id)
        except Sensor.DoesNotExist:
            return Http404("The sensor you requested does not exist.")

        if not request.user.is_part_of(sensor.team):
            return Http403("You do not have permission to view this sensor.")

        return sensor


class SensorDetail(AuthenticatedEndpoint, Detail):
    """
    Viewing a single sensor (GET)
    Modifying a sensor (PUT)
    Deleting a sensor (DELETE)

    @param sensor_id Sensor UUID
    """

    def get(self, request, sensor_id):
        sensor = self.get_sensor(request, sensor_id)

        if isinstance(sensor, Sensor):
            return SensorDetailPresenter(sensor).serialized
        else:
            return sensor

    def put(self, request, sensor_id):
        sensor = self.get_sensor(request, sensor_id)

        if not isinstance(sensor, Sensor):
            return sensor

        form = SensorForm(request.data, instance=sensor)

        if form.is_valid():
            form.save()
        else:
            return serialize([(k, v[0]) for k, v in form.errors.items()])

        return serialize(sensor)


class SensorAdvisories(AuthenticatedEndpoint, Detail):
    """
    Get a list of advisories for a single sensor (GET)

    @param sensor_id Sensor UUID

    """
    def get(self, request, sensor_id):
        sensor = self.get_sensor(request, sensor_id)

        if not isinstance(sensor, Sensor):
            return sensor

        objects = sensor.advisories.prefetch_related("rule") \
                                   .order_by("-created")

        # Parse Parameters
        per_page = safe_cast(request.GET.get("per_page"), int, default=100)
        page = safe_cast(request.GET.get("page"), int, default=1)

        pages = Paginator(objects, per_page)

        try:
            advisories = pages.page(page)
        except EmptyPage:
            return None

        return serialize({
            "advisories": AdvisoryPresenter(advisories.object_list).serialized,
            "page": page,
            "num_pages": pages.num_pages,
        })


class EventsList(AuthenticatedEndpoint):
    def get(self, request):
        """
        Return 50 events (GET)

        """
        team = request.user.team.identifier
        events = EventAPI().events_for_team(team)

        sensor_ids = [ e["sensor"] for e in events ]

        sensors = request.user.team.sensors.filter(uuid__in=sensor_ids)

        return EventPresenter(events).serialized(sensors)


class EventDetail(AuthenticatedEndpoint):
    def get(self, request, event_id):
        event = EventAPI().get_event(event_id)

        try:
            sensor = request.user.team.sensors.get(uuid=event['sensor'])
            event["sensor"] = sensor.uuid
            event["sensor_name"] = sensor.name
            event["sensor_groups"] = sensor.groups
        except Sensor.DoesNotExist:
            event["sensor"] = None
            event["sensor_name"] = None
            event["sensor_groups"] = []

        return EventPresenter(event).serialize