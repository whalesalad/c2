import os
import pprint

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "c2.settings")

from django.conf import settings

app = Celery('c2')

app.config_from_object(settings)
app.autodiscover_tasks(lambda: settings.CORE_APPS)