import jwt
import json
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.http import JsonResponse
from jwt_authentication.decorators import jwt_required
from django.conf import settings

User = get_user_model()

@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        group = None
        if role is not None:
            group = Group.objects.get(name=role)

        user = User.objects.create_user(username=username, password=password)
        if group is not None:
            user.groups.add(group)

        return JsonResponse({
            "user": {"id": user.id, "username": user.username},
            "status": "created"
        }, status=201)
    except Group.DoesNotExist:
        return JsonResponse({
            "error": "Data Invalid",
            "message": "invalid role",
            "status": "bad-request"
        }, status=400)
    except (ValueError, ValidationError, IntegrityError) as e:
        return JsonResponse({
            "error": "Data Invalid",
            "message": f"Invalid request body: {e}",
            "status": "bad-request"
        }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON",
            "message": "Invalid request body: Expecting valid JSON",
            "status": "bad-request"
        }, status=400)

@csrf_exempt
@jwt_required
@require_http_methods(["GET", "PUT", "DELETE"])
def user_detail_view(request, user_id):
    if request.method == 'GET':
        return show_user(request, user_id)
    elif request.method == 'DELETE':
        return delete_user(request, user_id)
    elif request.method == 'PUT':
        return update_user(request, user_id)
    else:
        return JsonResponse({
            "error": "Method Not Allowed",
            "message": "method not allowed for current path",
            "status": "not-found"
        }, status=405)

def show_user(request, user_id):
    visible_groups_filter = getattr(settings, "VISIBLE_GROUPS_FILTER", [])
    user = None

    if request.user.id != user_id:
        user = User.objects.filter(id=user_id).first()

        if user is None:
            return JsonResponse({
                "error": "User Not Found",
                "message": f"User not found with ID {user_id}",
                "status": "not-found"
            }, status=404)
    else:
        user = request.user

    groups = None
    if user.groups is not None and len(visible_groups_filter) > 0:
        groups = user.groups.filter(name__in=visible_groups_filter)

    user_data = {"id": user.id, "username": user.username }

    if groups is not None and len(groups) > 0:
        user_data = user_data | {"roles": [group.name for group in groups]}

    return JsonResponse({
        "user": user_data,
        "status": "success"
    }, status=200)

def update_user(request, user_id):
    if request.user.id != user_id:
        return JsonResponse({
            "error": "Unauthorized",
            "message": "current user not allowed to delete another user",
            "status": "unauthorized"
        }, status=401)

    try:
        user = request.user
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if username is not None:
            user.username = username

        if password is not None:
            user.password = password

        user.save()

        user_data = {"id": user.id, "username": user.username }
        return JsonResponse({
            "user": user_data,
            "status": "success"
        }, status=200)
    except (ValueError, IntegrityError, ValidationError):
        return JsonResponse({
            "error": "Data Invalid",
            "message": f"Invalid request body: {e}",
            "status": "bad-request"
        }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON",
            "message": "Invalid request body: Expecting valid JSON",
            "status": "bad-request"
        }, status=400)

def delete_user(request, user_id):
    if request.user.id != user_id:
        return JsonResponse({
            "error": "Unauthorized",
            "message": "current user not allowed to delete another user",
            "status": "unauthorized"
        }, status=401)

    user = request.user
    user_data = {"id": user.id, "username": user.username }
    try:
        user.delete()
        return JsonResponse({
            "user": user_data,
            "status": "deleted"
        }, status=200)
    except User.DoesNotExist:
        return JsonResponse({
            "error": "User Not Found",
            "message": f"User not found with ID {user_id}",
            "status": "not-found"
        }, status=404)
    except Exception:
        return JsonResponse({
            "error": "Server Error",
            "message": "something wrong",
            "status": "server-error"
        }, status=500)
