import time

from restless.views import Endpoint
from restless.http import Http403

class AuthenticatedEndpoint(Endpoint):
    def authenticate(self, request):
        if not request.user.is_authenticated():
            return Http403("You must be logged-in to access this resource.")

def epoch(datetime):
    return time.mktime(datetime.timetuple())