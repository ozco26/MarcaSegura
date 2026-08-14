from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
)
from werkzeug.security import generate_password_hash

from app.config.extensions import db
from app.models.mark import Mark
from app.models.user import User
from app.services.auth_service import authenticate_user
from app.services.decoradors import admin_required

web_auth_bp = Blueprint("web_auth", __name__)


@web_auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("El correo y la contraseña son obligatorios.", "danger")

        return render_template("auth/login.html")

    user = authenticate_user(email, password)

    if user is None:
        flash("Credenciales inválidas.", "danger")

        return render_template("auth/login.html")

    access_token = create_access_token(
        identity=str(user["id"]), additional_claims={"role": user["role"]}
    )

    response = redirect(url_for("web_auth.dashboard"))

    set_access_cookies(response, access_token)

    return response


@web_auth_bp.route("/dashboard")
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims["role"]

    # Estadísticas (ajusta según tus modelos)
    total_users = User.query.count()
    active_users = User.query.filter_by(status=True).count()
    # Por ahora, valores de ejemplo (luego con modelos reales)
    today_marks = 0
    today_incidents = 0

    if role == "admin":
        return render_template(
            "admin/dashboard.html",
            user_id=user_id,
            role=role,
            total_users=total_users,
            active_users=active_users,
            today_marks=today_marks,
            today_incidents=today_incidents,
        )
    else:
        claims = get_jwt()
        csrf_token = claims.get("csrf", "")
        user = User.query.get(user_id)
        marks = (
            Mark.query.filter_by(user_id=user.id).order_by(Mark.timestamp.desc()).all()
        )

        return render_template(
            "employee/dashboard.html",
            csrf_token=csrf_token,
            current_user=user,
            marks=marks,
            user_id=user_id,
            role=role,
        )
