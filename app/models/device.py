from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.config.extensions import db


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    device_uuid = db.Column(db.String(36), nullable=False, unique=True)

    status = db.Column(
        db.String(20), nullable=False, default="known"
    )  # 'known', 'authorized', 'blocked'

    first_seen = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("America/Costa_Rica")),
    )

    last_seen = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("America/Costa_Rica")),
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("America/Costa_Rica")),
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("America/Costa_Rica")),
        onupdate=datetime.now(ZoneInfo("America/Costa_Rica")),
    )

    user = db.relationship("User")
