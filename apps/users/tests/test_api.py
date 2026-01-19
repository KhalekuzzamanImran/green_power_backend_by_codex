import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_user_registration_api_success():
    client = APIClient()
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "StrongPass123!",
    }

    response = client.post("/api/users/register/", payload, format="json")

    assert response.status_code == 201
    assert response.data["username"] == "alice"
    assert response.data["email"] == "alice@example.com"
    assert "password" not in response.data


@pytest.mark.django_db
def test_user_registration_api_rejects_weak_password():
    client = APIClient()
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "short",
    }

    response = client.post("/api/users/register/", payload, format="json")

    assert response.status_code == 400
    assert "password" in response.data
