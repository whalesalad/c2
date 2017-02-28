from celery.utils.log import get_task_logger

from c2.celery_app import app

logger = get_task_logger(__name__)

@app.task
def sync_sensor_hostname(sensor):
    """
    Performs sync of sensor name with Snapshot Service.
    """
    sensor.name = sensor.get_hostname()

    if sensor.name:
        sensor.save()

@app.task
def sync_sensor_cloud_key(sensor):
    """
    Performs sync of sensor cloud_key with Snapshot Service.
    """
    sensor.cloud_key = sensor.get_cloud_key()

    if sensor.cloud_key:
        sensor.save()