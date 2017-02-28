from django.contrib import auth


class TokenAuthMiddleware(object):
    """
    Middleware for authenticating users based on a JWT token.

    The 'Authorization' header is used with a value of 'Bearer <token>'

    """
    def process_request(self, request):
        try:
            token_header = request.META['HTTP_AUTHORIZATION']
            token = token_header.split(' ')[1]
        except KeyError:
            return

        user = auth.authenticate(token=token)

        if user:
            request.user = user
