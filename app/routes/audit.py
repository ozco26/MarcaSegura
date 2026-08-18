from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import jwt_required

from app.models.device import Device
from app.models.mark import Mark
from app.models.user import User
from app.services.decoradors import admin_required

audit_bp = Blueprint(
    "audit",
    __name__,
    url_prefix="/admin/audit",
)


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

    devices = (
        Device.query.join(User)
        .filter(Device.status == "known")
        .order_by(Device.created_at.desc())
        .all()
    )

    return render_template(
        "admin/audit.html",
        marks=marks,
        users=users,
        devices=devices,
        selected_user_id=user_id,
    )


@audit_bp.route("/device/<int:device_id>/authorize", methods=["POST"])
@jwt_required()
@admin_required()
def authorize_device(device_id):

    device = Device.query.get_or_404(device_id)

    device.status = "authorized"

    from app.config.extensions import db

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Dispositivo autorizado correctamente.",
                "device_status": device.status,
            }
        ),
        200,
    )


@audit_bp.route("/device/<int:device_id>/block", methods=["POST"])
@jwt_required()
@admin_required()
def block_device(device_id):

    device = Device.query.get_or_404(device_id)

    device.status = "blocked"

    from app.config.extensions import db

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Dispositivo bloqueado correctamente.",
                "device_status": device.status,
            }
        ),
        200,
    )


@audit_bp.route("/incidents")
@jwt_required()
@admin_required()
def admin_incidents():

    from app.models.incident import Incident

    incidents = Incident.query.join(User).order_by(Incident.timestamp.desc()).all()

    return render_template(
        "admin/incidents.html",
        incidents=incidents,
    )
