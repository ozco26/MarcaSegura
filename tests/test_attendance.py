from datetime import time

from werkzeug.security import generate_password_hash

from app.config.extensions import db
from app.models.device import Device
from app.models.incident import Incident
from app.models.mark import Mark
from app.models.user import User


def test_mark_requires_authentication(client):
    response = client.post(
        "/attendance/mark",
        json={
            "device_uuid": "device-123",
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 401


def test_mark_without_data(authenticated_client):
    response = authenticated_client.post("/attendance/mark", json={})

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "No se recibieron datos."


def test_mark_requires_device_uuid(authenticated_client):
    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "El identificador del dispositivo es obligatorio."


def test_mark_requires_location(authenticated_client):
    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "device-123",
            "accuracy": 10,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "La ubicación es obligatoria."


def test_mark_requires_accuracy(authenticated_client):
    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "device-123",
            "latitude": 9.9281,
            "longitude": -84.0907,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["message"] == "La precisión de la ubicación es obligatoria."


def test_first_mark_is_entry(authenticated_client):
    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "device-123",
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert (
        data["message"] == "Marca registrada correctamente. "
        "El dispositivo ha sido registrado "
        "y está pendiente de autorización."
    )

    assert data["device_status"] == "known"
    assert data["mark"]["type"] == "entry"
    assert data["mark"]["latitude"] == 9.9281
    assert data["mark"]["longitude"] == -84.0907
    assert data["mark"]["accuracy"] == 10


def test_new_device_is_registered(authenticated_client, app):
    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "device-new-123",
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 201

    with app.app_context():
        device = Device.query.filter_by(device_uuid="device-new-123").first()

        assert device is not None
        assert device.status == "known"
        assert device.user_id == 1


def test_existing_device_is_reused(
    authenticated_client,
    user,
    app,
):
    with app.app_context():
        device = Device(
            user_id=user,
            device_uuid="device-existing-123",
            status="authorized",
        )

        db.session.add(device)
        db.session.commit()

        device_id = device.id

    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "device-existing-123",
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 201

    with app.app_context():
        devices = Device.query.filter_by(device_uuid="device-existing-123").all()

        assert len(devices) == 1
        assert devices[0].id == device_id


def test_foreign_device_is_rejected(
    authenticated_client,
    app,
):
    with app.app_context():

        other_user = User(
            name="Empleado",
            email="employee@test.com",
            password_hash=generate_password_hash("123456"),
            role="employee",
            status=True,
            entry_time=time(8, 0),
            exit_time=time(17, 0),
        )

        db.session.add(other_user)
        db.session.commit()

        device = Device(
            user_id=other_user.id,
            device_uuid="foreign-device-123",
            status="authorized",
        )

        db.session.add(device)
        db.session.commit()

    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "foreign-device-123",
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["device_status"] == "invalid"

    assert (
        data["message"] == "No se puede registrar la asistencia "
        "desde este dispositivo."
    )


def test_foreign_device_creates_incident(
    authenticated_client,
    app,
):
    with app.app_context():

        other_user = User(
            name="Empleado",
            email="employee2@test.com",
            password_hash=generate_password_hash("123456"),
            role="employee",
            status=True,
            entry_time=time(8, 0),
            exit_time=time(17, 0),
        )

        db.session.add(other_user)
        db.session.commit()

        device = Device(
            user_id=other_user.id,
            device_uuid="foreign-device-456",
            status="authorized",
        )

        db.session.add(device)
        db.session.commit()

    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "foreign-device-456",
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 403

    with app.app_context():

        incident = Incident.query.first()

        assert incident is not None
        assert incident.user_id == 1
        assert incident.severity == "high"

        assert (
            incident.description == "Se intentó registrar asistencia "
            "utilizando un dispositivo asociado "
            "a otro usuario."
        )


def test_blocked_device_is_rejected(
    authenticated_client,
    user,
    app,
):
    with app.app_context():

        device = Device(
            user_id=user,
            device_uuid="blocked-device-123",
            status="blocked",
        )

        db.session.add(device)
        db.session.commit()

    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "blocked-device-123",
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["device_status"] == "blocked"

    assert (
        data["message"] == "Este dispositivo está bloqueado "
        "y no puede registrar asistencia."
    )


def test_blocked_device_creates_incident(
    authenticated_client,
    user,
    app,
):
    with app.app_context():

        device = Device(
            user_id=user,
            device_uuid="blocked-device-456",
            status="blocked",
        )

        db.session.add(device)
        db.session.commit()

    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "blocked-device-456",
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 403

    with app.app_context():

        incident = Incident.query.first()

        assert incident is not None
        assert incident.user_id == 1
        assert incident.severity == "high"

        assert (
            incident.description == "Se intentó registrar asistencia "
            "utilizando un dispositivo bloqueado."
        )


def test_blocked_device_does_not_create_mark(
    authenticated_client,
    user,
    app,
):
    with app.app_context():

        device = Device(
            user_id=user,
            device_uuid="blocked-device-789",
            status="blocked",
        )

        db.session.add(device)
        db.session.commit()

        marks_before = Mark.query.count()

    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "blocked-device-789",
            "latitude": 9.9281,
            "longitude": -84.0907,
            "accuracy": 10,
        },
    )

    assert response.status_code == 403

    with app.app_context():

        marks_after = Mark.query.count()

        assert marks_after == marks_before


def test_mark_after_entry_is_exit(authenticated_client, user, app):
    with app.app_context():
        mark = Mark(
            user_id=user,
            type="entry",
            latitude=9.9281,
            longitude=-84.0907,
            accuracy=10,
            device_uuid="device-123",
        )

        db.session.add(mark)
        db.session.commit()

    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "device-456",
            "latitude": 9.9282,
            "longitude": -84.0908,
            "accuracy": 8,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert (
        data["message"]
        == "Marca registrada correctamente. El dispositivo ha sido registrado y está pendiente de autorización."
    )
    assert data["mark"]["type"] == "exit"


def test_mark_after_exit_is_entry(authenticated_client, user, app):
    with app.app_context():
        mark = Mark(
            user_id=user,
            type="exit",
            latitude=9.9281,
            longitude=-84.0907,
            accuracy=10,
            device_uuid="device-123",
        )

        db.session.add(mark)
        db.session.commit()

    response = authenticated_client.post(
        "/attendance/mark",
        json={
            "device_uuid": "device-456",
            "latitude": 9.9282,
            "longitude": -84.0908,
            "accuracy": 8,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert (
        data["message"]
        == "Marca registrada correctamente. El dispositivo ha sido registrado y está pendiente de autorización."
    )
    assert data["mark"]["type"] == "entry"
