import pytest

from app import create_app
from app.config.extensions import db


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
