from flask import Flask
from flask_migrate import Migrate
from app.database import db

migrate = Migrate()
 
def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.routes import routes_bp
    app.register_blueprint(routes_bp)

    return app
