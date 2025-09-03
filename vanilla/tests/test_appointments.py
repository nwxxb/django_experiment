from app.models import User, UserRole, Service, Appointment
from pytest_unordered import unordered
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token
import pytest

def test_appointments_create(client, db_session, service_factory, user_factory, bearer_token_dict_factory):
    now = datetime.now(timezone.utc)
    appointment_date = now + timedelta(days=7)
    doctor = user_factory(username="doctor_1", email="doctor@example.com", role=UserRole.DOCTOR)
    service = service_factory(name="Massage", address="New Jersey", doctor=doctor)
    patient = user_factory(username="patient_1", email="patient@example.com", role=UserRole.PATIENT)
    db_session.add(doctor)
    db_session.add(service)
    db_session.add(patient)
    db_session.commit()

    headers = {} | bearer_token_dict_factory(patient)
    request_data = { "service_id": service.id, "scheduled_at": appointment_date.timestamp() }
    response = client.post("/api/appointments", headers=headers, json=request_data)

    assert response.status_code == 201
    assert response.json["appointment"] == {
            "id": 1, "scheduled_at": appointment_date.timestamp(),
            "service": {"id": service.id, "name": service.name, "address": service.address},
            "doctor": {"id": doctor.id, "username": doctor.username, "email": doctor.email, "role": doctor.role.value},
            "patient": {"id": patient.id, "username": patient.username, "email": patient.email, "role": patient.role.value}
        }
    assert response.json["status"] == "created"
    appointment = db_session.get(Appointment, 1)
    assert appointment.to_dict(attach_assoc=['service', 'doctor', 'patient']) == {
            "id": 1, "scheduled_at": appointment_date.timestamp(),
            "service": {"id": service.id, "name": service.name, "address": service.address},
            "doctor": {"id": doctor.id, "username": doctor.username, "email": doctor.email, "role": doctor.role.value},
            "patient": {"id": patient.id, "username": patient.username, "email": patient.email, "role": patient.role.value}
        }

def test_appointments_index_all(client, db_session, appointment_factory, user_factory, bearer_token_dict_factory):
    current_user = user_factory(username="patient1", role=UserRole.PATIENT)
    patient2 = user_factory(username="patient2", role=UserRole.PATIENT)
    appointments = [
        appointment_factory(patient=current_user),
        appointment_factory(patient=patient2),
        appointment_factory(patient=current_user),
        appointment_factory(patient=patient2),
        appointment_factory(patient=current_user),
        appointment_factory(patient=patient2)
    ]

    db_session.add_all(appointments)
    db_session.commit()

    headers = {} | bearer_token_dict_factory(current_user)
    response = client.get(f"/api/appointments", headers=headers)

    assert response.status_code == 200
    assert response.json["appointments"] == unordered([
            appointments[0].to_dict(attach_assoc=['service', 'doctor']),
            appointments[2].to_dict(attach_assoc=['service', 'doctor']),
            appointments[4].to_dict(attach_assoc=['service', 'doctor'])
        ])
    assert response.json["status"] == "success"


def test_appointment_delete(client, db_session, appointment_factory, user_factory, bearer_token_dict_factory):
    current_user = user_factory(role=UserRole.PATIENT)

    appointment = appointment_factory(patient=current_user)
    db_session.add(appointment)
    db_session.commit()
    old_appointment = appointment
    old_service = appointment.service
    old_doctor = appointment.doctor
    old_patient = appointment.patient

    headers = {} | bearer_token_dict_factory(current_user)
    response = client.delete(f"/api/appointments/{appointment.id}", headers=headers)

    appointment = db_session.get(Appointment, appointment.id)
    assert appointment is None
    service = db_session.get(Service, old_service.id)
    assert service is not None
    doctor = db_session.get(User, old_doctor.id)
    assert doctor is not None
    patient = db_session.get(User, old_patient.id)
    assert patient is not None
    assert response.status_code == 200
    assert response.json["appointment"] == { "id": old_appointment.id, "scheduled_at": old_appointment.scheduled_at }
    assert response.json["status"] == "deleted"
