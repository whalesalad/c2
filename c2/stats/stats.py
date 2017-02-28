# TODO: Deprecate me or move me somewhere interesting...
from kairos import Timeseries

import time
import redis

from c2 import settings

REDIS = {
    'host': settings.REDIS_HOST,
    'port': settings.REDIS_PORT,
    'db': 0
}

REDIS_CLIENT = redis.StrictRedis(**REDIS)

class TimeseriesManager(object):
    client = REDIS_CLIENT

    INTERVALS= {
        'hour': {
            'step': 60 * 60,  # 60 minutes
            'steps': 24, # last 24 hours
        },
        'day': {
            'step': 60 * 60 * 24, # 1 Day
            'steps': 7 # Last 1 week
        },
        'week': {
            'step': 60 * 60 * 24 * 7, # 1 Week
            'steps': 4 # Last 1 Month (~4 weeks)
        },
        'month': {
            'step': 60 * 60 * 24 * 7 * 4, # 1 Month (~4 weeks)
            'step': 3 # Last 1 'Quarter'
        }
    }

    def __init__(self, team_id, series_type):
        self.team_id = team_id
        self.series = Timeseries(self.client, type=series_type, intervals=self.INTERVALS)

    def gen_cache_key(self, stat_name):
        return "%s~%s" % (self.team_id, stat_name)

    def insert(self, stat_name, value):
        cache_key = self.gen_cache_key(stat_name)
        self.series.insert(cache_key, value, timestamp=time.time())

    def query(self, stat_name, interval):
        cache_key = self.gen_cache_key(stat_name)
        return self.series.series(cache_key, interval)

