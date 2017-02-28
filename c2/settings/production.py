import os

from base import *

KAFKA_HOST = ""
KAFKA_PORT = 9092

REDIS_HOST = ""

STATSD_HOST = ""
STATSD_PORT = 8125

ALLOWED_HOSTS = '*'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public')
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OFFLINE = True

MIDDLEWARE_CLASSES += (
    'c2.utils.middleware.ElasticLoadBalancerSSLMiddleware',
)

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.postgresql_psycopg2',
        'HOST':         '',
        'NAME':         'c2',
        'USER':         '',
        'PASSWORD':     '',
        'PORT':         5432,
        'CONN_MAX_AGE': 10
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename':  '/var/log/c2/django.log',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['logfile', 'console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['logfile', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'c2.utils.middleware': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'c2.metadata': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        }
    },
}

BROKER_URL = 'redis://%s:%s/7' % (REDIS_HOST, REDIS_PORT, )
CELERY_RESULT_BACKEND = 'redis://%s:%s/8' % (REDIS_HOST, REDIS_PORT, )
