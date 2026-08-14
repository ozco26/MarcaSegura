from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.config.extensions import db


class Incident(db.Model):
    __tablename__ = "incidents"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # 'low', 'medium', 'high'
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(ZoneInfo("America/Costa_Rica")),
    )
    user = db.relationship("User", backref="incidents")
