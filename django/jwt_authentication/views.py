import jwt
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.http import JsonResponse
from .utils import JWTUtils

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            jwt_token = JWTUtils.generate_tokens(user)
            return JsonResponse({"access_token": jwt_token})
        else:
            return JsonResponse({
                "error": "Credential Invalid",
                "message": "invalid email or password",
                "status": "unauthorized"
            }, status=401)
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON",
            "message": "Invalid request body: Expecting valid JSON",
            "status": "bad-request"
        }, status=400)
