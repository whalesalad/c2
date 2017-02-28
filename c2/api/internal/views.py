import logging
import ujson as json

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from restless.http import Http201, Http403, JSONResponse
from restless.models import serialize

from c2.accounts.presenters import UserPresenter
from c2.accounts.auth.backends import TokenAuthBackend
from c2.accounts.models import APIKey

logger = logging.getLogger('console')

@csrf_exempt
@require_POST
def verify_token(request):
    backend = TokenAuthBackend()

    payload = json.loads(request.body)

    user = backend.authenticate(token=payload['token'])
    return JSONResponse(UserPresenter(user).serialized)


@csrf_exempt
@require_POST
def verify_access_key(request, access_key):
    """
    Verifies that an access_key is valid. Used inside of the sensor endpoint.

    """
    try:
        apikey = APIKey.objects.get(access_key=access_key)
    except APIKey.DoesNotExist:
        return Http403("The access_key is not valid.")

    return JSONResponse(serialize(apikey, fields=[
        'secret_key',
        ('identifier', lambda a: a.team.identifier),
    ]))