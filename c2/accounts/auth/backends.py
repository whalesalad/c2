import time

from django.conf import settings
from django.contrib.auth import get_user_model

from c2.services import TokenService

User = get_user_model()

class TokenAuthBackend(object):
    def authenticate(self, token=None):
        payload = TokenService().payload_for_token(token)

        if not payload:
            return None

        max_time = getattr(settings, "SESSION_EXPIRATION")
        if time.time() - payload['iat'] > max_time:
            return None

        return self.get_user(payload.get('uid', None))

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None