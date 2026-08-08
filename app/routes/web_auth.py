from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.services.auth_service import authenticate_user

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

    result = authenticate_user(email, password)

    if result is None:
        flash("Credenciales inválidas.", "danger")
        return render_template("auth/login.html")

    user = result["user"]

    session.clear()

    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["email"] = user["email"]
    session["role"] = user["role"]

    return redirect(url_for("web_auth.dashboard"))

@web_auth_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("web_auth.login"))

    return render_template(
        "employee/dashboard.html",
        user=session
    )