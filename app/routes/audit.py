from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.models.user import User
from app.models.mark import Mark

from app.services.decoradors import admin_required

audit_bp = Blueprint("audit", __name__, url_prefix="/admin/audit")


@audit_bp.route("/")
@jwt_required()
@admin_required()
def admin_genral():
    user_id = request.args.get("user_id")

    query = Mark.query

    if user_id:
        query = query.filter(Mark.user_id == user_id)

    marks = query.order_by(Mark.timestamp.desc()).all()

    users = User.query.order_by(User.name.asc()).all()

    return render_template(
        "admin/audit.html", marks=marks, users=users, selected_user_id=user_id
    )


@audit_bp.route("/incidents")
@jwt_required()
@admin_required()
def admin_incidents():
    from app.models.incident import Incident

    incidents = Incident.query.join(User).order_by(Incident.timestamp.desc()).all()
    return render_template("admin/incidents.html", incidents=incidents)
