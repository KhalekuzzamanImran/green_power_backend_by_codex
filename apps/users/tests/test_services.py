import pytest
from django.core.exceptions import ValidationError

from apps.users.services.user_service import register_user
from common.exceptions import UserAlreadyExistsError


@pytest.mark.django_db
def test_register_user_creates_user():
    user = register_user("alice", "alice@example.com", "StrongPass123!")
    assert user.id is not None
    assert user.username == "alice"
    assert user.email == "alice@example.com"


@pytest.mark.django_db
def test_register_user_rejects_duplicates():
    register_user("alice", "alice@example.com", "StrongPass123!")
    with pytest.raises(UserAlreadyExistsError):
        register_user("alice", "alice@example.com", "StrongPass123!")


@pytest.mark.django_db
def test_register_user_validates_password():
    with pytest.raises(ValidationError):
        register_user("alice", "alice@example.com", "short")
