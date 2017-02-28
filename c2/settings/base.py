import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

SECRET_KEY = '%+q66hfhhs+!nz9d37d$uvxktv(inb!fr0+=y#qh5=*3m-(n=8'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

VERMONT_HOST = None
SKYHOOK_HOST = None
KEYMASTER_HOST = None
GRAPH_HOST = None

SESSION_EXPIRATION = 24 * 60 * 60 * 7

DJANGO_APPS = (
    'django.contrib.admin.apps.AdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
)

THIRD_PARTY_APPS = (
    'django_extensions',
    'restless',
)

CORE_APPS = (
    'c2.rules',
    'c2.accounts',
    'c2.sensors',
    'c2.events',
    'c2.api',
    'c2.utils',
    # 'c2.playground',
    'c2.snapshot',
    'c2.stats',
    'c2.advisories',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CORE_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'c2.accounts.auth.middleware.TokenAuthMiddleware',
    'c2.api.middleware.JSONRequestMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.debug",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    # "c2.utils.context_processors.extra_template_context"
)

INTERNAL_IPS = '127.0.0.1'

ROOT_URLCONF = 'c2.urls'

WSGI_APPLICATION = 'c2.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql_psycopg2',
        'NAME':     'recon',
        'USER':     '',
        'PASSWORD': '',
        'HOST':     '',
        'PORT':     '',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = "America/Los_Angeles"

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/public/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
    os.path.join(PROJECT_ROOT, 'public')
)

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = (
    'c2.accounts.auth.backends.TokenAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

KAFKA_HOST = 'localhost'
KAFKA_PORT = 9092
KAFKA_EVENT_TOPIC = 'events'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_WEBSOCKETS_DB = 9

STATSD_HOST = 'localhost'
STATSD_PORT = 8125

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '%s:%s:1' % (REDIS_HOST, REDIS_PORT, ),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            }
        },
    },
    'advisory_cache': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '%s:%s:2' % (REDIS_HOST, REDIS_PORT, ),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 5,
            }
        },
    },
    'snapshot_cache': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '%s:%s:3' % (REDIS_HOST, REDIS_PORT, ),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 5,
            }
        },
    },
    'aws_cache': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '%s:%s:4' % (REDIS_HOST, REDIS_PORT, ),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 5,
            }
        },
    },
    'event_cache': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': '%s:%s:5' % (REDIS_HOST, REDIS_PORT, ),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 5,
            }
        },
    }
}

CACHES['assets'] = CACHES['default']

# For Celery.
# Database #7 for the base task broker
# Database #8 for storing results
BROKER_URL            = 'redis://%s:%s/7' % (REDIS_HOST, REDIS_PORT, )
CELERY_RESULT_BACKEND = 'redis://%s:%s/8' % (REDIS_HOST, REDIS_PORT, )

CELERYBEAT_SCHEDULE = {
    # 'sync-coverage-data-every-3-mins': {
        # 'task': 'c2.stats.tasks.sync_all_teams_coverage',
        # 'schedule': timedelta(minutes=3),
        # 'args': ()
    # },
    # 'send-sensor-counts-to-statsd': {
    #     'task': 'tasks.statsd_sensor_counts',
    #     'schedule': timedelta(minutes=5),
    # },
}

CELERY_TIMEZONE = 'UTC'
