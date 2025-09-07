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

def permission_required(permission_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(permission_name):
                return JsonResponse({
                    "error": "Permission Denied",
                    "message": f"You do not have the required permission: '{permission_name}'",
                    "status": "forbidden"
                }, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
