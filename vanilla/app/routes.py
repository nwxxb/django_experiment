from flask import Blueprint, jsonify

routes_bp = Blueprint('routes', __name__)

from app.api import api_bp
routes_bp.register_blueprint(api_bp, url_prefix='/api')
