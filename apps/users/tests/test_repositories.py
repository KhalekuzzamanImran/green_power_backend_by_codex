import pytest

from apps.users.repositories.user_repository import create_user


@pytest.mark.django_db
def test_create_user_persists_user():
    user = create_user("alice", "alice@example.com", "StrongPass123!")

    assert user.id is not None
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.check_password("StrongPass123!")
