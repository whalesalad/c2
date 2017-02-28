from django.db.models.signals import post_save
from django.dispatch import receiver

from c2.advisories.models import Advisory, Notification

@receiver(post_save, sender=Advisory)
def create_notifications(sender, instance, **kwargs):
    """
    Creates a read/unread notification for each member of a team.
    """
    for member in instance.team.members.all():
        Notification.objects.create(user=member, advisory=instance)
