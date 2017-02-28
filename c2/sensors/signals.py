from django.db.models.signals import pre_save
from django.dispatch import receiver

from c2.sensors.models import Sensor

@receiver(pre_save, sender=Sensor)
def set_properties_on_enrollment(sender, instance, **kwargs):
    """
    Tries to set the sensor's properties upon enrollment.

    """
    if not instance.created:
        instance.set_properties_from_snapshot()
