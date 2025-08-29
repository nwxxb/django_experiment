import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import db
from app.config import TestingConfig
from app.models import User, UserRole, Service

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
    def _user_factory(username, email=_sentinel, role=UserRole.PATIENT, password='password'):
        if email is _sentinel:
            email = f"{username}@example.com"

        user = User(username=username, email=email, role=role)
        user.set_password(password)

        return user
    return _user_factory

@pytest.fixture
def service_factory(user_factory):
    def _service_factory(name, address, doctor=_sentinel):
        if doctor is _sentinel:
            doctor = user_factory(username='doctor1', role=UserRole.DOCTOR)

        service = Service(name=name, address=address, doctor=doctor)

        return service
    return _service_factory
