from flask import Blueprint, jsonify, request

from app.services.auth_service import authenticate_user


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    result = authenticate_user(email, password)

    if result is None:
        return jsonify({
            "message": "Invalid credentials"
        }), 401

    return jsonify(result), 200