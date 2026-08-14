from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.config.extensions import db


class Mark(db.Model):
    __tablename__ = "marks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    device_uuid = db.Column(db.String(36), nullable=False)

    type = db.Column(db.String(10), nullable=False)  # 'entry' o 'exit'
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("America/Costa_Rica")),
    )
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    user = db.relationship("User", backref="marks")
