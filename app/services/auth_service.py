from werkzeug.security import check_password_hash

from app.models.user import User


def authenticate_user(email, password):

    user = User.query.filter_by(email=email).first()

    if user is None:
        return None

    if not user.status:
        return None

    if not check_password_hash(user.password_hash, password):
        return None

    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
