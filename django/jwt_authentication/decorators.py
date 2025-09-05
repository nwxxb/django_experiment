from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser):
            return JsonResponse({
                "error": "Authentication Required",
                "message": "Valid JWT token required",
                "status": "unauthorized"
            }, status=401)

        return view_func(request, *args, **kwargs)
    return wrapper
