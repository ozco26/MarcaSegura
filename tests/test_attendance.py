from app.config.extensions import db
from app.models.mark import Mark


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

    assert data["message"] == "Entrada registrada correctamente."
    assert data["mark"]["type"] == "entry"
    assert data["mark"]["latitude"] == 9.9281
    assert data["mark"]["longitude"] == -84.0907
    assert data["mark"]["accuracy"] == 10


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

    assert data["message"] == "Salida registrada correctamente."
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

    assert data["message"] == "Entrada registrada correctamente."
    assert data["mark"]["type"] == "entry"
