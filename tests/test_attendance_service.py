import pytest

from app.config.extensions import db
from app.models.mark import Mark
from app.services.attendance_service import CreateMark, LastMark


def test_create_mark(app):
    with app.app_context():
        mark = CreateMark(
            user_id=1,
            mark_type="entry",
            latitude=9.9281,
            longitude=-84.0907,
            accuracy=10.5,
            device_uuid="device-123",
        )

        assert mark.id is not None
        assert mark.user_id == 1
        assert mark.type == "entry"
        assert mark.latitude == 9.9281
        assert mark.longitude == -84.0907
        assert mark.accuracy == 10.5
        assert mark.device_uuid == "device-123"


def test_last_mark_returns_latest_mark(app):
    with app.app_context():
        first_mark = Mark(
            user_id=1,
            type="entry",
            latitude=9.9281,
            longitude=-84.0907,
            accuracy=10,
            device_uuid="device-123",
        )

        second_mark = Mark(
            user_id=1,
            type="exit",
            latitude=9.9282,
            longitude=-84.0908,
            accuracy=8,
            device_uuid="device-123",
        )

        db.session.add_all([first_mark, second_mark])
        db.session.commit()

        last_mark = LastMark(1)

        assert last_mark is not None
        assert last_mark.type == "exit"
        assert last_mark.id == second_mark.id


def test_last_mark_returns_none_when_user_has_no_marks(app):
    with app.app_context():
        result = LastMark(999)

        assert result is None
