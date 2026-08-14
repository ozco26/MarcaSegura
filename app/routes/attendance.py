from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.config.extensions import db
from app.models.mark import Mark
from app.services.attendance_service import CreateMark, LastMark

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")


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
            jsonify({"message": "El identificador del dispositivo es obligatorio."}),
            400,
        )
    if latitude is None or longitude is None:
        return jsonify({"message": "La ubicación es obligatoria."}), 400
    if accuracy is None:
        return jsonify({"message": "La precisión de la ubicación es obligatoria."}), 400
    last_mark = LastMark(user_id)
    if last_mark is None or last_mark.type == "exit":
        mark_type = "entry"
    else:
        mark_type = "exit"
    new_mark = CreateMark(
        user_id, mark_type, latitude, longitude, accuracy, device_uuid
    )

    message = (
        "Entrada registrada correctamente."
        if mark_type == "entry"
        else "Salida registrada correctamente."
    )

    return (
        jsonify(
            {
                "message": message,
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
