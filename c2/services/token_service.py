import jwt
import time

from django.conf import settings

class TokenService(object):
    FALLBACK_TOKEN = "XXX-YYY-ZZZ-REPLACE-MEEE"
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TokenService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.secret = getattr(settings, "SECRET_KEY", self.FALLBACK_TOKEN)

    def token_for_user(self, user):
        return jwt.encode({
            'iat': time.time(),
            'uid': user.id,
            'email': user.email,
        }, self.secret, "HS512")

    def payload_for_token(self, token):

        try:
            return jwt.decode(token, self.secret)
        except jwt.DecodeError:
            return None