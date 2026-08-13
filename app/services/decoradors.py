from functools import wraps

from flask import abort
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()  # Verifica el token
            claims = get_jwt()
            if claims.get("role") != "admin":
                abort(403, description="Acceso solo para administradores")
            return fn(*args, **kwargs)

        return decorator

    return wrapper
