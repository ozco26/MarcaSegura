from werkzeug.security import check_password_hash

from app.config.extensions import db
from app.models.user import User
from app.services.email_service import notify_admins_failed_attempts
from app.services.incident_service import CreateIncident

FAILED_ATTEMPTS_THRESHOLD = 5


def authenticate_user(email, password):

    user = User.query.filter_by(email=email).first()

    if user is None:
        return None

    if not user.status:
        return None

    if not check_password_hash(user.password_hash, password):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= FAILED_ATTEMPTS_THRESHOLD:
            CreateIncident(
                user_id=user.id,
                description=(
                    f"{user.failed_login_attempts} intentos fallidos de "
                    f"autenticación consecutivos."
                ),
                severity="high",
            )
            notify_admins_failed_attempts(user, user.failed_login_attempts)
            user.failed_login_attempts = 0

        db.session.commit()

        return None

    user.failed_login_attempts = 0
    db.session.commit()

    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}