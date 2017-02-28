import os

from base import *

ALLOWED_HOSTS = '*'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public')

REDIS_HOST = os.environ.get('REDIS_PORT_6379_TCP_ADDR', '127.0.0.1')
REDIS_PORT = os.environ.get('REDIS_PORT_6379_TCP_PORT', 6379)

DATABASES = {
    'default': {
        'ENGINE'    : 'django.db.backends.postgresql_psycopg2',
        'NAME'      : 'c2',
        'USER'      : 'postgres',
        'PASSWORD'  : '',
        'HOST'      : os.environ.get('POSTGRES_PORT_5432_TCP_ADDR', 'localhost'),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

BROKER_URL = 'redis://%s:%s/7' % (REDIS_HOST, REDIS_PORT, )
CELERY_RESULT_BACKEND = 'redis://%s:%s/8' % (REDIS_HOST, REDIS_PORT, )