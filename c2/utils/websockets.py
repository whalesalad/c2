import ujson as json
import redis
import logging

from django.conf import settings

logger = logging.getLogger('c2.websockets')

class TeamBroadcaster():
    def __init__(self, team):
        self.team = team
        self.connection = redis.StrictRedis(host=settings.REDIS_HOST,
                                            port=settings.REDIS_PORT,
                                            db=settings.REDIS_WEBSOCKETS_DB)

    def send(self, event, payload):
        message = {
            'event': event,
            'payload': payload
        }

        self.connection.publish(self.team.identifier, json.dumps(message))
