from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from .utils import JWTUtils
import json

User = get_user_model()

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = JWTUtils.validate_token(token)
            if payload:
                try:
                    user = User.objects.get(id=payload['sub'])
                    request.user = user
                    request.jwt_payload = payload
                except User.DoesNotExist:
                    request.user = AnonymousUser()
                    request.jwt_payload = None
            else:
                request.user = AnonymousUser()
                request.jwt_payload = None
        else:
            # don't block other auth middleware (e.g. session-based auth)
            pass
