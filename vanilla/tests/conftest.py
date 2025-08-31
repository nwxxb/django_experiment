import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import db
from app.config import TestingConfig
from app.models import User, UserRole, Service, Appointment
from datetime import datetime

@pytest.fixture
def app():
    app = create_app(TestingConfig)

    # Create tables
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        yield db.session
        # Rollback any changes after each test
        db.session.rollback()

# model factory
_sentinel = object()

@pytest.fixture
def user_factory():
    count = 0
    def _user_factory(username=_sentinel, email=_sentinel, role=UserRole.PATIENT, password='password'):
        nonlocal count
        count += 1

        if username is _sentinel:
            username = f"person{count}"

        if email is _sentinel:
            email = f"{username}@example.com"

        user = User(username=username, email=email, role=role)
        user.set_password(password)

        return user
    return _user_factory

_service_factory_count = 0

@pytest.fixture
def service_factory(user_factory):
    count = 0
    def _service_factory(name=_sentinel, address='An Address', doctor=_sentinel):
        nonlocal count
        count += 1

        if name is _sentinel:
            name = f"service-{count}"

        if doctor is _sentinel:
            doctor = user_factory(role=UserRole.DOCTOR)

        service = Service(name=name, address=address, doctor=doctor)

        return service
    return _service_factory

@pytest.fixture
def appointment_factory(service_factory, user_factory):
    def _appointment_factory(
            scheduled_at=datetime.now().timestamp(),
            service=_sentinel, doctor=_sentinel,
            patient=user_factory(role=UserRole.PATIENT)
            ):
        if service is _sentinel and doctor is _sentinel:
            doctor = user_factory(role=UserRole.DOCTOR)
            service = service_factory(doctor=doctor)
        elif service is not _sentinel and doctor is _sentinel:
            doctor = service.doctor
        elif service is _sentinel and doctor is not _sentinel:
            service = service_factory(doctor=doctor)

        appointment = Appointment(scheduled_at=scheduled_at, service=service, doctor=doctor, patient=patient)

        return appointment
    return _appointment_factory
