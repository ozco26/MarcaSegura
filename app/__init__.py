from flask import Flask

from app import models
from app.config.config import Config
from app.config.extensions import db, jwt, migrate
from app.routes.auth import auth_bp
from app.routes.web_auth import web_auth_bp


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(web_auth_bp)

    @app.route("/")
    def index():
        return "Marca Segura funcionando"

    return app