from app.services.device_service import (
    authorize_device,
    block_device,
)
from app.models.device import Device
from app.config.extensions import db


def test_block_device(app, user):
    with app.app_context():
        device = Device(
            user_id=user,
            device_uuid="22222222-2222-2222-2222-222222222222",
            status="known",
        )

        db.session.add(device)
        db.session.commit()

        block_device(device)

        assert device.status == "blocked"


def test_authorize_device(app, user):
    with app.app_context():
        device = Device(
            user_id=user,
            device_uuid="11111111-1111-1111-1111-111111111111",
            status="known",
        )

        db.session.add(device)
        db.session.commit()

        authorize_device(device)

        assert device.status == "authorized"


def test_admin_can_authorize_device(
    authenticated_client,
    user,
):
    device = Device(
        user_id=user,
        device_uuid="33333333-3333-3333-3333-333333333333",
        status="known",
    )

    db.session.add(device)
    db.session.commit()

    response = authenticated_client.post(f"/admin/audit/device/{device.id}/authorize")

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == ("Dispositivo autorizado correctamente.")
    assert data["device_status"] == "authorized"

    db.session.refresh(device)

    assert device.status == "authorized"


def test_admin_can_block_device(
    authenticated_client,
    user,
):
    device = Device(
        user_id=user,
        device_uuid="44444444-4444-4444-4444-444444444444",
        status="known",
    )

    db.session.add(device)
    db.session.commit()

    response = authenticated_client.post(f"/admin/audit/device/{device.id}/block")

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == ("Dispositivo bloqueado correctamente.")
    assert data["device_status"] == "blocked"

    db.session.refresh(device)

    assert device.status == "blocked"


def test_authorize_nonexistent_device(authenticated_client):
    response = authenticated_client.post("/admin/audit/device/999999/authorize")

    assert response.status_code == 404


def test_employee_cannot_authorize_device(
    employee_client,
    user,
):
    device = Device(
        user_id=user,
        device_uuid="55555555-5555-5555-5555-555555555555",
        status="known",
    )

    db.session.add(device)
    db.session.commit()

    response = employee_client.post(f"/admin/audit/device/{device.id}/authorize")

    assert response.status_code == 403

    db.session.refresh(device)

    assert device.status == "known"


def test_employee_cannot_block_device(
    employee_client,
    user,
):
    device = Device(
        user_id=user,
        device_uuid="66666666-6666-6666-6666-666666666666",
        status="known",
    )

    db.session.add(device)
    db.session.commit()

    response = employee_client.post(f"/admin/audit/device/{device.id}/block")

    assert response.status_code == 403

    db.session.refresh(device)

    assert device.status == "known"
