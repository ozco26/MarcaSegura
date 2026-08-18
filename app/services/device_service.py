from datetime import datetime
from zoneinfo import ZoneInfo

from app.config.extensions import db
from app.models.device import Device

COSTA_RICA_TZ = ZoneInfo("America/Costa_Rica")


def get_device(device_uuid):
    return Device.query.filter_by(device_uuid=device_uuid).first()


def register_device(user_id, device_uuid):
    now = datetime.now(COSTA_RICA_TZ)

    device = Device(
        user_id=user_id,
        device_uuid=device_uuid,
        status="known",
        first_seen=now,
        last_seen=now,
    )

    db.session.add(device)
    db.session.flush()

    return device


def update_device_last_seen(device):
    device.last_seen = datetime.now(COSTA_RICA_TZ)


def authorize_device(device):
    device.status = "authorized"


def block_device(device):
    device.status = "blocked"
