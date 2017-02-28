from py2neo import Graph

from django.core.cache import caches
from django.core.paginator import Paginator, EmptyPage

from restless.models import serialize
from restless.http import Http404

from c2.advisories.models import Advisory, Notification
from c2.advisories.presenters import (AdvisoryPresenter,
                                      AdvisoryDetailPresenter,
                                      NotificationPresenter)

from c2.advisories.graph_query import GraphQuery

from c2.events.presenters import EventPresenter
from c2.events import EventAPI

from c2.snapshot import SnapshotAPI

from c2.api.utils import AuthenticatedEndpoint

from c2.utils import safe_cast


cache = caches["advisory_cache"]

class AdvisoryList(AuthenticatedEndpoint):
    """
    Return a list of advisories. (GET)
    """
    def get(self, request):
        """
        @query page     Requested page number
        @query per_page Number of results per page

        """
        objects = request.user.team.advisories \
                                   .prefetch_related("sensor", "rule") \
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


class AdvisoryDetail(AuthenticatedEndpoint):
    """
    Return a detailed information about an advisory. (GET)

    @param advisory_id Advisory ID number

    """
    def get(self, request, advisory_id):
        a = request.user.team.advisories \
                             .prefetch_related("sensor", "rule") \
                             .get(pk=advisory_id)

        return AdvisoryDetailPresenter(a).serialized


class AdvisoryEvents(AuthenticatedEndpoint):
    def get(self, request, advisory_id):
        
        a = request.user.team.advisories.get(pk=advisory_id)

        return EventPresenter(a.events).serialized(a.sensors)

class AdvisoryProcessInfo(AuthenticatedEndpoint):
    def get(self, request, sensor_id):
        result = cache.get("%s.process_info" % sensor_id)

        if result:
            return result

        else:
            process_info = SnapshotAPI(request.user.team.identifier).sensor_process_tree(sensor_id)
            cache.set("%s.process_info" % sensor_id, process_info, 300)

            return serialize(process_info)


class NotificationList(AuthenticatedEndpoint):
    """
    Return a list of unread advisories for a user. (GET)

    """
    def get(self, request):
        notifications = request.user.notifications \
                            .filter(unread=True) \
                            .prefetch_related("advisory") \
                            .order_by("-created")

        return NotificationPresenter(notifications).serialized

        # return NotificationPresenter(notifications).serialized


class NotificationDetail(AuthenticatedEndpoint):
    """
    Mark a notification as read (PUT)

    @param advisory_id Notification ID

    """
    def put(self, request, advisory_id):
        """
        Notifications will never need to be directly accessed or modified,
        so a PUT request will simply serve to toggle read/unread status

        """

        try:
            notification = request.user.notifications.get(advisory_id=advisory_id)
        except Notification.DoesNotExist:
            return Http404("Notification not found.")

        notification.unread = not notification.unread
        notification.save()

        return NotificationPresenter(notification).serialized