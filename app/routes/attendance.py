from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.config.extensions import db
from app.models.user import User
from app.services.attendance_service import CreateMark, LastMark
from app.services.device_service import (
    get_device,
    register_device,
    update_device_last_seen,
)
from app.services.email_service import notify_admins_unusual_location
from app.services.incident_service import CreateIncident
from app.services.location_service import is_unusual_location

COSTA_RICA_TZ = ZoneInfo("America/Costa_Rica")

attendance_bp = Blueprint(
    "attendance",
    __name__,
    url_prefix="/attendance",
)


@attendance_bp.route("/mark", methods=["POST"])
@jwt_required()
def mark():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"message": "No se recibieron datos."}), 400

    device_uuid = data.get("device_uuid")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    accuracy = data.get("accuracy")

    if not device_uuid:
        return (
            jsonify(
                {"message": ("El identificador del dispositivo " "es obligatorio.")}
            ),
            400,
        )

    if latitude is None or longitude is None:
        return jsonify({"message": "La ubicación es obligatoria."}), 400

    if accuracy is None:
        return (
            jsonify({"message": ("La precisión de la ubicación " "es obligatoria.")}),
            400,
        )

    device = get_device(device_uuid)

    device_is_new = False

    if device is None:

        device = register_device(
            user_id=user_id,
            device_uuid=device_uuid,
        )

        device_is_new = True

    else:
        if device.user_id != int(user_id):

            CreateIncident(
                user_id=user_id,
                description=(
                    "Se intentó registrar asistencia "
                    "utilizando un dispositivo asociado "
                    "a otro usuario."
                ),
                severity="high",
            )

            db.session.commit()

            return (
                jsonify(
                    {
                        "message": (
                            "No se puede registrar la asistencia "
                            "desde este dispositivo."
                        ),
                        "device_status": "invalid",
                    }
                ),
                403,
            )

        if device.status == "blocked":

            CreateIncident(
                user_id=user_id,
                description=(
                    "Se intentó registrar asistencia "
                    "utilizando un dispositivo bloqueado."
                ),
                severity="high",
            )

            db.session.commit()

            return (
                jsonify(
                    {
                        "message": (
                            "Este dispositivo está bloqueado "
                            "y no puede registrar asistencia."
                        ),
                        "device_status": "blocked",
                    }
                ),
                403,
            )

        update_device_last_seen(device)

    last_mark = LastMark(user_id)

    current_timestamp = datetime.now(COSTA_RICA_TZ)

    is_unusual, distance_km = is_unusual_location(
        last_mark, latitude, longitude, current_timestamp
    )

    if is_unusual:
        alert_user = User.query.get(int(user_id))

        CreateIncident(
            user_id=user_id,
            description=(
                f"Marca de asistencia desde una ubicación inusual. "
                f"Distancia respecto a la última marca: {distance_km} km."
            ),
            severity="medium",
        )

        notify_admins_unusual_location(
            alert_user,
            f"Distancia de {distance_km} km respecto a la última marca "
            f"registrada, en un lapso de tiempo poco realista para ese "
            f"desplazamiento.",
        )

    if last_mark is None or last_mark.type == "exit":
        mark_type = "entry"
    else:
        mark_type = "exit"

    new_mark = CreateMark(
        user_id,
        mark_type,
        latitude,
        longitude,
        accuracy,
        device_uuid,
    )
    db.session.commit()
    if device_is_new:
        message = (
            "Marca registrada correctamente. "
            "El dispositivo ha sido registrado "
            "y está pendiente de autorización."
        )
    else:

        message = (
            "Entrada registrada correctamente."
            if mark_type == "entry"
            else "Salida registrada correctamente."
        )

    return (
        jsonify(
            {
                "message": message,
                "device_status": device.status,
                "mark": {
                    "id": new_mark.id,
                    "type": new_mark.type,
                    "latitude": new_mark.latitude,
                    "longitude": new_mark.longitude,
                    "accuracy": new_mark.accuracy,
                    "timestamp": new_mark.timestamp.isoformat(),
                },
            }
        ),
        201,
    )