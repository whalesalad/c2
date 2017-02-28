from django.db import models

class ActiveOnlyManager(models.Manager):
    """
    Makes the default queryset for objects with an 'is_active' field
    only return those objects.

    """

    def get_queryset(self):
        return super(ActiveOnlyManager, self).get_queryset().filter(is_active=True)
