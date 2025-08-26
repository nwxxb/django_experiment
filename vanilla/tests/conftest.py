import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    # Set the Flask app to testing mode
    app.config["TESTING"] = True
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
    })

    # Create tables
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Clean up temp file
    os.close(db_fd)
    os.unlink(db_path)

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
