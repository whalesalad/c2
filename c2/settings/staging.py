import os

from base import *

KAFKA_HOST = "stage-kafka-1.internal.egsense.net"

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
        'HOST':         'stage-rds-001.cgnsddeu5x1t.us-west-2.rds.amazonaws.com',
        'NAME':         'c2',
        'USER':         'root',
        'PASSWORD':     'FragByffunvebTiShrue',
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
        'logstash': {
            'format' : "[C2] [%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
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
        },
        # 'syslog': {
        #     'class': 'logging.handlers.SysLogHandler',
        #     'formatter': 'logstash',
        #     'facility': 'user',
        #     # uncomment next line if rsyslog works with unix socket only (UDP reception disabled)
        #     #'address': '/dev/log'
        # }
        'logstash': {
            'level': 'DEBUG',
            'class': 'logstash.LogstashHandler',
            'host': 'ip-172-31-39-55.us-west-2.compute.internal',
            'port': 5959,
            'version': 1,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logstash', 'console'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['logstash', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'c2.utils.middleware': {
            'handlers': ['logstash'],
            'level': 'INFO',
            'propagate': True,
        },
        'c2.metadata': {
            'handlers': ['logstash'],
            'level': 'INFO',
            'propagate': True,
        }
    },
}

BROKER_URL = 'redis://%s:%s/7' % (REDIS_HOST, REDIS_PORT, )
CELERY_RESULT_BACKEND = 'redis://%s:%s/8' % (REDIS_HOST, REDIS_PORT, )