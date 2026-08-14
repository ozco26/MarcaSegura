from app.config.extensions import db
from app.models.mark import Mark


def CreateMark(user_id, mark_type, latitude, longitude, accuracy, device_uuid):
    new_mark = Mark(
        user_id=user_id,
        type=mark_type,
        latitude=float(latitude),
        longitude=float(longitude),
        accuracy=float(accuracy),
        device_uuid=device_uuid,
    )
    db.session.add(new_mark)
    db.session.commit()

    return new_mark


def LastMark(user_id):
    last_mark = (
        Mark.query.filter_by(user_id=user_id).order_by(Mark.timestamp.desc()).first()
    )
    return last_mark
