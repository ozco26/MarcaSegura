import pytest

from datetime import time

from werkzeug.security import generate_password_hash

from app import create_app
from app.config.extensions import db
from app.models.user import User


class TestConfig:
    TESTING = True

    SECRET_KEY = "test-secret-key-32-bytes-long"
    JWT_SECRET_KEY = "test-jwt-secret-key-32-bytes-long"

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = False

    JWT_COOKIE_SECURE = False
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = "Lax"

    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_CHECK_FORM = True


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    with app.app_context():
        user = User(
            name="Administrador",
            email="admin@test.com",
            password_hash=generate_password_hash("123456"),
            role="admin",
            status=True,
            entry_time=time(8, 0),
            exit_time=time(17, 0),
        )

        db.session.add(user)
        db.session.commit()

        return user.id


@pytest.fixture
def authenticated_client(client, user):
    response = client.post(
        "/login",
        data={
            "email": "admin@test.com",
            "password": "123456",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    csrf_token = None

    for cookie in response.headers.getlist("Set-Cookie"):
        if "csrf_access_token=" in cookie:
            csrf_token = cookie.split("csrf_access_token=")[1]
            csrf_token = csrf_token.split(";")[0]
            break

    assert csrf_token is not None

    client.environ_base["HTTP_X_CSRF_TOKEN"] = csrf_token

    return client
