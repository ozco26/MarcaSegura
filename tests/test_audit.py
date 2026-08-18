import pytest

from app.config.extensions import db
from app.models.user import User


@pytest.fixture
def employee_client(client, user):
    user_obj = db.session.get(User, user)

    user_obj.role = "employee"
    db.session.commit()

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


def test_audit_requires_authentication(client):
    response = client.get("/admin/audit/")

    assert response.status_code in (401, 302)


def test_admin_can_view_audit(authenticated_client):
    response = authenticated_client.get("/admin/audit/")

    assert response.status_code == 200


def test_audit_accepts_user_filter(authenticated_client, user):
    response = authenticated_client.get(f"/admin/audit/?user_id={user}")

    assert response.status_code == 200


def test_employee_cannot_view_audit(employee_client):
    response = employee_client.get("/admin/audit/")

    assert response.status_code == 403


def test_incidents_requires_authentication(client):
    response = client.get("/admin/audit/incidents")

    assert response.status_code in (401, 302)


def test_admin_can_view_incidents(authenticated_client):
    response = authenticated_client.get("/admin/audit/incidents")

    assert response.status_code == 200


def test_employee_cannot_view_incidents(employee_client):
    response = employee_client.get("/admin/audit/incidents")

    assert response.status_code == 403
