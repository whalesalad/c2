from collections import Counter
from restless.models import serialize

from django.db.models import Count, Q

from c2.rules.models import Rule
from c2.sensors.models import Cluster

from c2.api.utils import AuthenticatedEndpoint
from c2.stats import TimeseriesManager
from c2.snapshot import SnapshotAPI


class AssetStats(AuthenticatedEndpoint):
    """
    Query for Fleet Asset Monitoring Data (GET)

    """
    def get(self, request):
        sensors = request.user.team.sensors.all()

        snapshot = SnapshotAPI(request.user.team.identifier)

        state = snapshot.state
        clusters = snapshot.clusters
        assets = snapshot.cloud_information

        cluster_counts = Counter()
        group_counts = Counter()
        hosts = Counter()

        # Populate cluster statistics
        for uuid, members in clusters.iteritems():
            cluster, created = Cluster.objects.get_or_create(uuid=uuid, team=request.user.team)
            cluster_counts[cluster.name] += len(members)

        # Add AWS tag information to group list
        for key, asset in assets.iteritems():
            for key, value in asset["tags"].iteritems():
                if key != "Name":
                    group = "AWS - %s" % value
                    group_counts[group] += 1

        hosts["monitored"] = 0
        for s in sensors:
            hosts["monitored"] += 1

            # Populate groups statistics
            if s.groups:
                for g in s.groups:
                    group_counts[g] += 1

            # Remove from asset list to prevent duplicate entry
            assets.pop(s.cloud_key, None)

            # Check online/offline status
            status = state.get(s.uuid, {}).get("activity", {}).get("is_connected")
            if status:
                hosts["active"] += 1
            else:
                hosts["inactive"] += 1

        # All remaining assets are "unmonitored"
        hosts["unmonitored"] = len(assets.keys())

        hosts["total"] = hosts["monitored"] + hosts["unmonitored"]

        return serialize({
            "hosts": hosts,
            "groups": [{"name": name, "count": count} for name, count in group_counts.iteritems()],
            "clusters": [{"name": name, "count": count} for name, count in cluster_counts.iteritems()]
        })

class EventStats(AuthenticatedEndpoint):
    def get(self, request):
        return


class AdvisoryStats(AuthenticatedEndpoint):
    def get(self, request):
        sensor_id = request.GET.get("sensor")

        param = Q()

        if sensor_id:
            param = Q(sensor=sensor_id)

        rules_count = request.user.team.advisories \
                                       .filter(param) \
                                       .prefetch_related("rule") \
                                       .values("rule") \
                                       .annotate(Count("rule")) \
                                       .order_by()

        rule_map = {}
        for r in Rule.objects.values("id", "name").all():
            rule_map[r["id"]] = r["name"]

        advisory_total = request.user.team.advisories \
                                          .filter(param) \
                                          .count()
        type_data = []

        for a in rules_count:
            type_data.append({
                "name": rule_map[a["rule"]],
                "count": a["rule__count"],
            })

        return serialize({
            "total": advisory_total,
            "types": type_data,
        })


def tame_results(data, key):
    values = []
    for item, value in data.iteritems():
        result = transform_data(item, value)
        values.append(result)

    return { "key": key, "values": values }

def transform_data(item, value):
    total_intervals = 0
    total_count = 0

    # Created a weight average of coverage for the interval
    for num, count in value.iteritems():
        total_count += (int(num) * count)
        total_intervals += count

    try:
        value = total_count / total_intervals
    except:
        value = 0

    return [item, value]


class AssetTimeseriesStats(AuthenticatedEndpoint):
    """
    Query for Asset Timeseries Data (GET)

    """
    def get(self, request):
        # Pull request information
        interval = request.GET.get("interval", "hour")
        series_type = request.GET.get("type", "histogram")

        team_id = request.user.team.identifier
        manager = TimeseriesManager(team_id, series_type)

        monitored = manager.query("monitored",interval)
        unmonitored = manager.query("unmonitored",interval)

        mon = tame_results(monitored, "monitored")
        unmon = tame_results(unmonitored, "unmonitored")

        return serialize([mon, unmon])


class ClusterTimeseriesStats(AuthenticatedEndpoint):
    """
    Query for Cluster Timeseries Data (GET)
    """
    def get(self, request):
        interval = request.GET.get("interval", "hour")
        series_type = request.GET.get("type", "histogram")

        team_id = request.user.team.identifier
        clusters = request.user.team.clusters.all()

        manager = TimeseriesManager(team_id, series_type)

        results = []

        for cluster in clusters:
            stat = manager.query(cluster.uuid, interval)
            results.append(tame_results(stat, cluster.name))

        return serialize(results)


class EventTimeseriesStats(AuthenticatedEndpoint):
    """
    Query for Event Timeseries Data (GET)
    """
    def get(self, request):
        interval = request.GET.get("interval", "hour")
        series_type = request.GET.get("type", "histogram")
        return {}


class AdvisoryTimeseriesStats(AuthenticatedEndpoint):
    """
    Query for Advisory Timeseries Data (GET)
    """
    def get(self, request):
        interval = request.GET.get("interval", "hour")
        series_type = request.GET.get("type", "histogram")

        team_id = request.user.team.identifier
        manager = TimeseriesManager(team_id, series_type)

        results = []

        for rule in Rule.objects.all():
            stat = manager.query(rule.slug, interval)
            results.append(tame_results(stat, rule.name))

        return serialize(results)
