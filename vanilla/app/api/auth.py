from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from app.database import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("signin", methods=['POST'])
def signin():
    if not request.json:
        return jsonify({
            "error": "Create Failed",
            "message": "No JSON data provided",
            "status": "bad-request"
        }), 400

    data = request.json
    required_keys = ['email', 'password']
    is_request_body_valid = all(key in data and data[key] is not None for key in required_keys)

    if not is_request_body_valid:
        return jsonify({
            "error": "Login Failed",
            "message": "Invalid Request Payload",
            "status": "bad-request"
        }), 400

    user = db.session.query(User).filter_by(email=data.get("email")).first()

    if user is None or not user.check_password(data.get("password")):
        return jsonify({
            "error": "Credential Invalid",
            "message": "invalid email or password",
            "status": "unauthorized"
        }), 401

    claims = { "role": user.role.value }
    access_token = create_access_token(identity=user.id, additional_claims=claims)

    return jsonify({"user": user.to_dict(), "access_token": access_token, "status": "signed-in"}), 200
