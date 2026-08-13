from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.models.user import User
from app.services.decoradors import admin_required

audit_bp = Blueprint("audit", __name__, url_prefix="/admin/audit")


@audit_bp.route("/")
@jwt_required()
@admin_required()
def admin_genral():
    from app.models.mark import Mark

    marks = Mark.query.join(User).order_by(Mark.timestamp.desc()).all()
    return render_template("admin/audit.html", marks=marks)


@audit_bp.route("/incidents")
@jwt_required()
@admin_required()
def admin_incidents():
    from app.models.incident import Incident

    incidents = Incident.query.join(User).order_by(Incident.timestamp.desc()).all()
    return render_template("admin/incidents.html", incidents=incidents)
