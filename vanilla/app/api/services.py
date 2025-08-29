from flask import Blueprint, jsonify, request
from app.database import db
from app.models import User, UserRole, Service

services_bp = Blueprint('services', __name__)

@services_bp.route("", methods=['GET'])
def index_service():
    # services = db.session.get(Service, service_id)
    services = Service.query.all()
    services_dict = []
    for service in services:
        services_dict.append(service.to_dict())

    return jsonify({"services": services_dict, "status": "success"})

@services_bp.route("", methods=['POST'])
def create_service():
    if not request.json:
        return jsonify({
            "error": "Create Failed",
            "message": "No JSON data provided",
            "status": "bad-request"
        }), 400

    data = request.json
    required_keys = ['name', 'address', 'doctor_id']
    is_request_body_valid = all(key in data and data[key] is not None for key in required_keys)

    if not is_request_body_valid:
        return jsonify({
            "error": "Create Failed",
            "message": "Invalid Request Payload",
            "status": "bad-request"
        }), 400

    doctor_id = data.get('doctor_id')
    doctor = db.session.get(User, doctor_id)
    if doctor is None or doctor.role != UserRole.DOCTOR:
        return jsonify({
            "error": "doctor not found",
            "message": f"No user with doctor role exists with ID {doctor_id}",
            "status": "not-found"
        }), 404

    service = Service(
            name=data.get('name'),
            address=data.get('address'),
            doctor=doctor
    )
    db.session.add(service)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Create Failed",
            "message": "Service already exist",
            "status": "conflict"
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")

    return jsonify({"service": service.to_dict(), "status": "created"}), 201

@services_bp.route("/<int:service_id>", methods=['GET'])
def show_service(service_id):
    service = db.session.get(Service, service_id)
    if service is None:
        return jsonify({
            "error": "Service not found",
            "message": f"No service exists with ID {service_id}",
            "status": "not-found"
        }), 404

    return jsonify({"service": service.to_dict(), "status": "success"})

@services_bp.route("/<int:service_id>", methods=['PUT'])
def update_service(service_id):
    if not request.json:
        return jsonify({
            "error": "Update Failed",
            "message": "No JSON data provided",
            "status": "bad-request"
        }), 400

    service = db.session.get(Service, service_id)
    if service is None:
        return jsonify({
            "error": "Service not found",
            "message": f"No service exists with ID {service_id}",
            "status": "not-found"
        }), 404

    data = request.json

    if 'name' in data and data['name'] is not None:
        service.name = data.get('name')

    if 'address' in data and data['address'] is not None:
        service.address = data.get('address')

    if 'doctor_id' in data and data['doctor_id'] is not None:
        doctor_id = data.get('doctor_id')
        doctor = db.session.get(User, doctor_id)
        print("==============")
        print(doctor)
        print("==============")
        if doctor is None or doctor.role != UserRole.DOCTOR:
            return jsonify({
                "error": "doctor not found",
                "message": f"No user with doctor role exists with ID {doctor_id}",
                "status": "not-found"
            }), 404
        service.doctor = doctor

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")

    return jsonify({"service": service.to_dict(), "status": "updated"})

@services_bp.route("/<int:service_id>", methods=['DELETE'])
def delete_service(service_id):
    service = db.session.get(Service, service_id)
    if service is None:
        return jsonify({
            "error": "Service not found",
            "message": f"No service exists with ID {service_id}",
            "status": "not-found"
        }), 404

    db.session.delete(service)
    db.session.commit()
    return jsonify({"service": service.to_dict(attach_assoc=False), "status": "deleted"})

