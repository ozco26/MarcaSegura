from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.config.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(150), nullable=False, unique=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="employee")

    status = db.Column(db.Boolean, nullable=False, default=True)

    entry_time = db.Column(db.Time, nullable=False)

    exit_time = db.Column(db.Time, nullable=False)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("America/Costa_Rica")),
    )
