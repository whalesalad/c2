from collections import Counter

from c2.celery_app import app

from c2.accounts.models import Team
from c2.advisories.models import Advisory
from c2.sensors.models import Sensor, Cluster

from c2.stats import TimeseriesManager
from c2.snapshot import SnapshotAPI
from c2.events import EventAPI

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

event_to_rule_mapping = {
    'anomalous_process_behavior': 'process-anomaly',
    'anomalous_package': 'package-anomaly',
}

@app.task
def sync_all_teams_coverage():
    """
    Sync coverage statistics and save series data to redis.
    """
    teams = Team.objects.all()

    for team in teams:
        identifier = team.identifier

        sync_team_coverage.apply_async(args=(identifier, ))
        sync_team_cluster_stats.apply_async(args=(identifier, ))
        sync_team_advisory_stats.apply_async(args=(identifier, ))

@app.task
def sync_team_coverage(identifier):
    logger.info("Syncing coverage data information for %s" % identifier)
    team = Team.objects.get(identifier=identifier)

    snapshot = SnapshotAPI(identifier)
    assets = snapshot.cloud_information

    monitored = 0
    # Build up monitored assets stats and remove catalogued server
    # from known assets lists
    for s in team.sensors.all():
        monitored += 1
        assets.pop(s.cloud_key, None)

    unmonitored = len(assets.keys())

    manager = TimeseriesManager(identifier, 'histogram')
    manager.insert('monitored', monitored)
    manager.insert('unmonitored', unmonitored)

@app.task
def sync_team_cluster_stats(identifier):
    logger.info("Syncing cluster data information for %s" % identifier)
    team = Team.objects.get(identifier=identifier)

    snapshot = SnapshotAPI(identifier)

    sensors = Sensor.objects.filter(team=team)
    clusters = snapshot.clusters

    manager = TimeseriesManager(identifier, 'histogram')
    cluster_stats = {}

    for sensor in sensors:
        for uuid, members in clusters.iteritems():
            cluster, created = Cluster.objects.get_or_create(uuid=uuid, team=team)
            if not cluster_stats.get(cluster.uuid, None):
                cluster_stats[cluster.uuid] = 0

            if sensor.uuid in members:
                cluster_stats[cluster.uuid] += 1

    for name, count in cluster_stats.iteritems():
        if count:
            manager.insert(name, count)

@app.task
def flush_event_stats(event_stats, advisory_stats):
    for team, stats in event_stats.iteritems():
        manager = TimeseriesManager(team, 'histogram')
        for event_type, count in stats.iteritems():
            manager.insert(event_type, count)

    for team, stats in advisory_stats.iteritems():
        manager = TimeseriesManager(team, 'histogram')
        for name, count in stats.iteritems():
            slug = event_to_rule_mapping.get('name')
            manager.insert(slug, count)

# @app.task
# def sync_team_advisory_stats(identifier, stats):
#     logger.info("Syncing coverage data information for %s" % identifier)
#     team = Team.objects.get(identifier=identifier)

#     counts = Counter()
#     for a in team.advisories.all():
#         counts[a.rule.slug] += 1

#     manager = TimeseriesManager(identifier, 'histogram')

#     for rule, count in counts.iteritems():
#         manager.insert(rule, count)

