"""WSGI config for c2."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "c2.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
