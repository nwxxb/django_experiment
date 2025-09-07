import jwt
import json
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from jwt_authentication.decorators import jwt_required, permission_required
from django.conf import settings
from .models import Service, Appointment

User = get_user_model()

@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('appointments_api.add_service')
def create_service(request):
    try:
        data = json.loads(request.body)
        name = data.get("name")
        address = data.get("address")
        doctor_id = data.get("doctor_id")
        if doctor_id is None or not User.objects.filter(id=doctor_id).exists():
            return JsonResponse({
                "error": "Data Invalid",
                "message": f"Doctor not found",
                "status": "not-found"
            }, status=404)

        service = Service.objects.create(name=name, address=address, doctor_id=doctor_id)
        return JsonResponse({
            "service": {
                "id": service.id, "name": service.name, "address": service.address,
                "doctor": { "id": service.doctor.id, "username": service.doctor.username }
            },
            "status": "created"
        }, status=201)
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
@require_http_methods(["GET"])
@jwt_required
@permission_required('appointments_api.view_service')
def show_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        return JsonResponse({
            "service": {
                "id": service.id, "name": service.name, "address": service.address,
                "doctor": { "id": service.doctor.id, "username": service.doctor.username }
            },
            "status": "success"
        }, status=200)
    except Service.DoesNotExist:
        return JsonResponse({
            "error": "Not Found",
            "message": f"Service not found with id {service_id}",
            "status": "not-found"
        }, status=404)

@csrf_exempt
@require_http_methods(["GET"])
@jwt_required
@permission_required('appointments_api.view_service')
def show_all_services(request):
    services = Service.objects.all()
    return JsonResponse({
        "services": [
            {
                "id": service.id, "name": service.name, "address": service.address,
                "doctor": { "id": service.doctor.id, "username": service.doctor.username }
            } for service in services
        ],
        "status": "success"
    }, status=200)

@csrf_exempt
@require_http_methods(["PUT"])
@jwt_required
@permission_required('appointments_api.change_service')
def update_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)

        data = json.loads(request.body)
        name = data.get("name")
        address = data.get("address")
        doctor_id = data.get("doctor_id")
        doctor = None

        if doctor_id is not None:
            doctor = User.objects.get(id=doctor_id)

        if name is not None:
            service.name = name

        if address is not None:
            service.address = address

        if doctor_id is not None and doctor is not None:
            service.doctor = doctor

        service.save()

        return JsonResponse({
            "service": {
                "id": service_id, "name": service.name, "address": service.address,
                "doctor": {"id": service.doctor.id, "username": service.doctor.username}
            },
            "status": "updated"
        }, status=200)
    except (ValueError, ValidationError, IntegrityError) as e:
        return JsonResponse({
            "error": "Data Invalid",
            "message": f"Invalid request body: {e}",
            "status": "bad-request"
        }, status=400)
    except Service.DoesNotExist:
        return JsonResponse({
            "error": "Not Found",
            "message": f"Service not found with id {service_id}",
            "status": "not-found"
        }, status=404)
    except User.DoesNotExist:
        return JsonResponse({
            "error": "Data Invalid",
            "message": f"Doctor not found",
            "status": "not-found"
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON",
            "message": "Invalid request body: Expecting valid JSON",
            "status": "bad-request"
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
@jwt_required
@permission_required('appointments_api.delete_service')
def delete_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        service.delete()
        return JsonResponse({
            "service": {
                "id": service_id, "name": service.name, "address": service.address,
            },
            "status": "deleted"
        }, status=200)
    except Service.DoesNotExist:
        return JsonResponse({
            "error": "Not Found",
            "message": f"Service not found with id {service_id}",
            "status": "not-found"
        }, status=404)

@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
@permission_required('appointments_api.add_appointment')
def create_appointment(request):
    try:
        data = json.loads(request.body)
        scheduled_at = data.get("scheduled_at")
        service_id = data.get("service_id")
        service = Service.objects.get(id=service_id)

        appointment = Appointment.objects.create(
                scheduled_at=float(scheduled_at), service=service,
                doctor=service.doctor, patient=request.user)

        return JsonResponse({
            "appointment": {
                "id": appointment.id, "scheduled_at": appointment.scheduled_at,
                "service": { "id": appointment.service.id, "name": appointment.service.name, "address": appointment.service.address },
                "doctor": { "id": appointment.doctor.id, "username": appointment.doctor.username },
                "patient": { "id": appointment.patient.id, "username": appointment.patient.username }
            },
            "status": "created"
        }, status=201)
    except (ValueError, ValidationError, IntegrityError) as e:
        return JsonResponse({
            "error": "Data Invalid",
            "message": f"Invalid request body: {e}",
            "status": "bad-request"
        }, status=400)
    except Service.DoesNotExist:
        return JsonResponse({
            "error": "Not Found",
            "message": f"Service not found with id {service_id}",
            "status": "not-found"
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "Invalid JSON",
            "message": "Invalid request body: Expecting valid JSON",
            "status": "bad-request"
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
@jwt_required
@permission_required('appointments_api.view_appointment')
def show_all_appointments(request):
    appointments = request.user.appointments.all()
    return JsonResponse({
        "appointments": [
            {
                "id": appointment.id, "scheduled_at": float(appointment.scheduled_at),
                "service": { "id": appointment.service.id, "name": appointment.service.name, "address": appointment.service.address },
                "doctor": { "id": appointment.doctor.id, "username": appointment.doctor.username },
                "patient": { "id": appointment.patient.id, "username": appointment.patient.username }
            } for appointment in appointments
        ],
        "status": "success"
    }, status=200)

@csrf_exempt
@require_http_methods(["DELETE"])
@jwt_required
@permission_required('appointments_api.delete_appointment')
def delete_appointment(request, appointment_id):
    try:
        appointment = request.user.appointments.get(id=appointment_id)
        appointment.delete()
        return JsonResponse({
            "appointments": {
                    "id": appointment_id, "scheduled_at": float(appointment.scheduled_at),
            },
            "status": "deleted"
        }, status=200)
    except Appointment.DoesNotExist:
        return JsonResponse({
            "error": "Not Found",
            "message": f"Appointment not found with id {appointment_id}",
            "status": "not-found"
        }, status=404)
