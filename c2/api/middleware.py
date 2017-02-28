from django import http

class JSONRequestMiddleware(object):
    """
    Sets the 'is_json' property of request objects for content negotiation.
    """
    def process_request(self, request):
        request.is_json = (request.META.get('HTTP_ACCEPT', None) == 'application/json')


class CORSHeadersMiddleware(object):
    """
    Sets CORS Headers:
        'Access-Control-Allow-Origin': '*'
        'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
    """
    def process_request(self, request):
        if request.method == 'OPTIONS':
            response = http.HttpResponse()
            return response

        return None

    def process_response(self, request, response):

        allowed_headers = (
            'x-requested-with',
            'content-type',
            'accept',
            'origin',
            'authorization',
            'x-csrftoken',
            'user-agent',
            'accept-encoding',
        )

        response['Access-Control-Allow-Headers'] = ', '.join(allowed_headers)
        response['Access-Control-Allow-Origin'] = '*'
        return response
