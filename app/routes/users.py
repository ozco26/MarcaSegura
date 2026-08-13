from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash

from app.config.extensions import db
from app.models.user import User
from app.services.decoradors import admin_required

users_bp = Blueprint("users", __name__, url_prefix="/admin/users")


@users_bp.route("/", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])
@admin_required()
def users():
    claims = get_jwt()

    csrf_token = claims.get("csrf", "")
    edit_user = None
    user_id = request.args.get("edit")

    if user_id:
        edit_user = User.query.get(user_id)
        if not edit_user:
            flash("Usuario no encontrado", "danger")
            return redirect(url_for("users.users"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        status = request.form.get("status") == "on"
        entry_time = request.form.get("entry_time")
        exit_time = request.form.get("exit_time")
        user_id = request.form.get("user_id")

        # Validaciones
        if not all([name, email, role, entry_time, exit_time]):
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for("users.users"))

        # Verificar email único (excepto si es el mismo usuario)
        existing_user = User.query.filter(User.email == email).first()
        if existing_user and (not user_id or existing_user.id != int(user_id)):
            flash("El correo ya está registrado", "danger")
            return redirect(url_for("users.users"))

        try:
            entry_time_obj = datetime.strptime(entry_time, "%H:%M").time()
            exit_time_obj = datetime.strptime(exit_time, "%H:%M").time()
        except ValueError:
            flash("Formato de hora inválido. Use HH:MM", "danger")
            return redirect(url_for("users.users"))

        if user_id:  # Edición
            user = User.query.get(user_id)
            if not user:
                flash("Usuario no encontrado", "danger")
                return redirect(url_for("users.users"))

            user.name = name
            user.email = email
            if password:  # Si se envía nueva contraseña, la actualiza
                user.password_hash = generate_password_hash(password)
            user.role = role
            user.status = status
            user.entry_time = entry_time_obj
            user.exit_time = exit_time_obj

            db.session.commit()
            flash("Usuario actualizado exitosamente", "success")
        else:  # Creación
            if not password:
                flash("La contraseña es obligatoria", "danger")
                return redirect(url_for("users.users"))

            hashed_password = generate_password_hash(password)
            new_user = User(
                name=name,
                email=email,
                password_hash=hashed_password,
                role=role,
                status=status,
                entry_time=entry_time_obj,
                exit_time=exit_time_obj,
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Usuario creado exitosamente", "success")

        return redirect(url_for("users.users"))

    users = User.query.all()
    return render_template(
        "admin/users.html", users=users, csrf_token=csrf_token, edit_user=edit_user
    )


@users_bp.route("/delete/<int:user_id>", methods=["POST"])
@jwt_required(locations=["cookies"])
@admin_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("users.users"))

    # Evitar que un admin se elimine a sí mismo
    if str(user.id) == get_jwt_identity():
        flash("No puedes eliminarte a ti mismo", "danger")
        return redirect(url_for("users.users"))

    db.session.delete(user)
    db.session.commit()
    flash(f"Usuario {user.name} eliminado correctamente", "success")
    return redirect(url_for("users.users"))
