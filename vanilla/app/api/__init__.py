from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route("/ping")
def ping():
    return jsonify({"ping": "pong"})

# from app.api import auth
# from app.api import users
# from app.api import services
# from app.api import appointments
