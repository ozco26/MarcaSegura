from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager

from app import models  ##para que jale las migraciones
from app.config.config import Config
from app.config.extensions import db, jwt, migrate
from app.routes.audit import audit_bp
from app.routes.users import users_bp
from app.routes.web_auth import web_auth_bp


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(web_auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(audit_bp)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for("web_auth.login"))

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return redirect(url_for("web_auth.login"))

    @app.route("/login")
    def index():
        return "Marca Segura funcionando"

    return app
