from flask import Blueprint, jsonify, request
from app.database import db
from app.models import User, UserRole
from sqlalchemy.exc import IntegrityError

users_bp = Blueprint('users', __name__)

@users_bp.route("", methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({
            "error": "Create Failed",
            "message": "No JSON data provided",
            "status": "bad-request"
        }), 400

    data = request.json
    required_keys = ['username', 'email', 'role', 'password']
    is_request_body_valid = all(key in data and data[key] is not None for key in required_keys)

    if not is_request_body_valid:
        return jsonify({
            "error": "Create Failed",
            "message": "Invalid Request Payload",
            "status": "bad-request"
        }), 400

    user = User(
            username=data.get('username'),
            email=data.get('email'),
            role=UserRole(data.get('role'))
    )
    user.set_password(data.get('password'))
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Create Failed",
            "message": "User already exist",
            "status": "conflict"
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")

    return jsonify({"user": user.to_dict(), "status": "created"}), 201

@users_bp.route("/<int:user_id>", methods=['GET'])
def show_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({
            "error": "User not found",
            "message": f"No user exists with ID {user_id}",
            "status": "not-found"
        }), 404

    return jsonify({"user": user.to_dict(), "status": "success"})

@users_bp.route("/<int:user_id>", methods=['PUT'])
def update_user(user_id):
    if not request.json:
        return jsonify({
            "error": "Update Failed",
            "message": "No JSON data provided",
            "status": "bad-request"
        }), 400

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({
            "error": "User not found",
            "message": f"No user exists with ID {user_id}",
            "status": "not-found"
        }), 404

    data = request.json

    if 'username' in data and data['username'] is not None:
        user.username = data.get('username')

    if 'email' in data and data['email'] is not None:
        user.email = data.get('email')

    if 'role' in data and data['role'] is not None:
        user.role = UserRole(data.get('role'))

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")

    return jsonify({"user": user.to_dict(), "status": "updated"})

@users_bp.route("/<int:user_id>", methods=['DELETE'])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({
            "error": "User not found",
            "message": f"No user exists with ID {user_id}",
            "status": "not-found"
        }), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"user": user.to_dict(), "status": "deleted"})

