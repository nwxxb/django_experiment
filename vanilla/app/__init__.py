from flask import Flask
from flask_migrate import Migrate
from app.database import db

migrate = Migrate()
 
def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)

    if not app.config['SECRET_KEY']:
        raise ValueError("No SECRET_KEY set current environment")

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.routes import routes_bp
    app.register_blueprint(routes_bp)

    return app
