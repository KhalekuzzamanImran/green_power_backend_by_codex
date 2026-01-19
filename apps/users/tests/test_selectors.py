import pytest

from apps.users.models import User
from apps.users.selectors.user_selector import get_existing_user_identifiers


@pytest.mark.django_db
def test_get_existing_user_identifiers_returns_match():
    User.objects.create_user(username="alice", email="alice@example.com", password="StrongPass123!")

    result = get_existing_user_identifiers("alice", "alice@example.com")

    assert result == ("alice", "alice@example.com")


@pytest.mark.django_db
def test_get_existing_user_identifiers_returns_none_for_missing():
    result = get_existing_user_identifiers("missing", "missing@example.com")

    assert result is None
