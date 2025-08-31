from flask import Blueprint, jsonify, request
from app.database import db
from app.models import User, UserRole, Service, Appointment
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route("", methods=['GET'])
@jwt_required()
def index_appointment():
    jwt_sid = get_jwt_identity()
    current_user = db.session.get(User, jwt_sid)

    if current_user is None or current_user.role != UserRole.PATIENT:
        return jsonify({
            "error": "Create Failed",
            "message": "Current logged in user not found or not a patient",
            "status": "bad-request"
        }), 401

    appointments = current_user.appointments

    appointments_dict = []
    for appointment in appointments:
        appointments_dict.append(appointment.to_dict(attach_assoc=['service', 'doctor']))

    return jsonify({"appointments": appointments_dict, "status": "success"})

@appointments_bp.route("", methods=['POST'])
@jwt_required()
def create_service():
    if not request.json:
        return jsonify({
            "error": "Create Failed",
            "message": "No JSON data provided",
            "status": "bad-request"
        }), 400

    jwt_sid = get_jwt_identity()
    current_user = db.session.get(User, jwt_sid)
    if current_user is None or current_user.role != UserRole.PATIENT:
        return jsonify({
            "error": "Create Failed",
            "message": "Current logged in user not found or not a patient",
            "status": "bad-request"
        }), 401

    data = request.json
    required_keys = ['scheduled_at', 'service_id']
    is_request_body_valid = all(key in data and data[key] is not None for key in required_keys)

    if not is_request_body_valid:
        return jsonify({
            "error": "Create Failed",
            "message": "Invalid Request Payload",
            "status": "bad-request"
        }), 400

    service_id = data.get('service_id')
    service = db.session.get(Service, service_id)
    if service is None:
        return jsonify({
            "error": "service not found",
            "message": f"No service with ID {service_id}",
            "status": "not-found"
        }), 404

    appointment = Appointment(
            scheduled_at=float(data.get('scheduled_at')),
            service=service,
            doctor=service.doctor,
            patient=current_user
    )
    db.session.add(appointment)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Create Failed",
            "message": "Appointment already exist",
            "status": "conflict"
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")

    return jsonify({
        "appointment": appointment.to_dict(
            attach_assoc=['service', 'doctor', 'patient']
            ), "status": "created"
        }), 201

@appointments_bp.route("/<int:appointment_id>", methods=['DELETE'])
@jwt_required()
def delete_appointment(appointment_id):
    jwt_sid = get_jwt_identity()
    current_user = db.session.get(User, jwt_sid)
    if current_user is None or current_user.role != UserRole.PATIENT:
        return jsonify({
            "error": "Create Failed",
            "message": "Current logged in user not found or not a patient",
            "status": "bad-request"
        }), 401

    appointment = db.session.query(Appointment).filter_by(
            id=appointment_id,
            patient_id=current_user.id
    ).first()
    if appointment is None:
        return jsonify({
            "error": "Appointment not found",
            "message": f"No appointment exists with ID {appointment_id}",
            "status": "not-found"
        }), 404

    db.session.delete(appointment)
    db.session.commit()
    return jsonify({"appointment": appointment.to_dict(), "status": "deleted"})

