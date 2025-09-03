from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.database import db
from app.models import User, UserRole
import logging.config
import logging
from sqlalchemy import log as sqlalchemy_log

migrate = Migrate()
 
def create_app(config_object):
    # Patch to avoid duplicated-and-propagated logging from sqlalchemy
    sqlalchemy_log._add_default_handler = lambda x: None

    logging.config.dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'loggers': {
            'sqlalchemy': {
                'level': 'INFO',
                'handlers': ['wsgi'],
                'propagate': False
            },
            'sqlalchemy.orm': {
                'level': 'WARNING',
                'handlers': ['wsgi'],
                'propagate': False
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__)
    app.config.from_object(config_object)

    if not app.config['SECRET_KEY']:
        raise ValueError("No SECRET_KEY set current environment")

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        if "sub" not in jwt_data or "role" not in jwt_data:
            return None

        identity = jwt_data["sub"]
        role = jwt_data["role"]

        return User.query.filter_by(id=identity, role=UserRole(role)).one_or_none()

    from app.routes import routes_bp
    app.register_blueprint(routes_bp)

    return app
