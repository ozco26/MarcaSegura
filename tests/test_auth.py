from datetime import time

from werkzeug.security import generate_password_hash

from app.config.extensions import db
from app.models.user import User


def create_user(
    name="Administrador",
    email="admin@test.com",
    password="123456",
    role="admin",
    status=True,
):
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        status=status,
        entry_time=time(8, 0),
        exit_time=time(17, 0),
    )

    db.session.add(user)
    db.session.commit()

    return user


def test_login_success(client, app):
    with app.app_context():
        create_user()

    response = client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "123456",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")


def test_login_invalid_password(client, app):
    with app.app_context():
        create_user()

    response = client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "incorrecta",
        },
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert b"Credenciales inv" in response.data


def test_login_nonexistent_user(client):
    response = client.post(
        "/login",
        data={
            "email": "noexiste@test.com",
            "password": "123456",
        },
    )

    assert response.status_code == 200
    assert b"Credenciales inv" in response.data


def test_login_inactive_user(client, app):
    with app.app_context():
        create_user(
            email="inactive@test.com",
            status=False,
        )

    response = client.post(
        "/login",
        data={
            "email": "inactive@test.com",
            "password": "123456",
        },
    )

    assert response.status_code == 200
    assert b"Credenciales inv" in response.data


def test_login_without_email(client):
    response = client.post(
        "/login",
        data={
            "password": "123456",
        },
    )

    assert response.status_code == 200
    assert b"correo" in response.data.lower()


def test_login_without_password(client):
    response = client.post(
        "/login",
        data={
            "email": "admin@test.com",
        },
    )

    assert response.status_code == 200
    assert b"contrase" in response.data.lower()


def test_authenticated_user_can_access_dashboard(client, app):
    with app.app_context():
        create_user()

    login_response = client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "123456",
        },
    )

    assert login_response.status_code == 302

    response = client.get("/dashboard")

    assert response.status_code == 200


def test_dashboard_requires_authentication(client):
    response = client.get("/dashboard")

    assert response.status_code == 401


def create_user_employee(
    name="User",
    email="User@test.com",
    password="123456",
    role="employee",
    status=True,
):
    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        status=status,
        entry_time=time(8, 0),
        exit_time=time(17, 0),
    )

    db.session.add(user)
    db.session.commit()

    return user


def test_login_success_employee(client, app):
    with app.app_context():
        create_user(
            name="Empleado",
            email="employee@test.com",
            role="employee",
        )

    response = client.post(
        "/login",
        data={
            "email": "employee@test.com",
            "password": "123456",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")


def test_authenticated_user_can_access_dashboard_employee(
    client,
    app,
):
    with app.app_context():
        create_user(
            name="Empleado",
            email="employee@test.com",
            role="employee",
        )

    login_response = client.post(
        "/login",
        data={
            "email": "employee@test.com",
            "password": "123456",
        },
        follow_redirects=False,
    )

    assert login_response.status_code == 302

    response = client.get("/dashboard")

    assert response.status_code == 200
