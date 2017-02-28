import statsd
import pprint

from django.db.models import Count

from celery.utils.log import get_task_logger
from celery.decorators import periodic_task

from c2.celery_app import app
from c2.accounts.models import Team
from c2.sensors.models import Sensor
from c2.settings import STATSD_HOST, STATSD_PORT

logger = get_task_logger(__name__)

statsd.Connection.set_defaults(host=STATSD_HOST, port=STATSD_PORT)

@app.task
def statsd_sensor_counts():
    """
    A periodic task to gather metrics for the number of sensors
    per team and push them to the statsd instance on the monitoring
    server

    """
    gauge = statsd.Gauge('sensor.saas.sensors')

    gauge.send('count', Sensor.objects.count())

    for team in Team.objects.annotate(num_sensors=Count('sensors')):
        gauge.send("team.%s.count" % team.identifier, team.num_sensors)

    logger.info("Logged sensor counts to statsd.")
