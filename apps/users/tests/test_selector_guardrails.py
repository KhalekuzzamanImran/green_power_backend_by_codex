import pytest
from django.core.cache import cache

from apps.users.models import User
from apps.users.services.user_service import deactivate_user, register_user, update_user
from apps.users.selectors.user_selector import get_user_by_id_cached


@pytest.mark.django_db
def test_register_user_does_not_use_replica_read_selector(monkeypatch):
    from apps.users.services import user_service

    def fail_if_called(*args, **kwargs):
        raise AssertionError("read selector used in write path")

    monkeypatch.setattr(user_service, "get_existing_user_identifiers", fail_if_called, raising=False)

    register_user("alice", "alice@example.com", "StrongPass123!")


@pytest.mark.django_db
def test_write_selector_is_used_for_registration(monkeypatch):
    from apps.users.services import user_service

    called = {"ok": False}

    def wrapped(*args, **kwargs):
        called["ok"] = True
        return None

    monkeypatch.setattr(user_service, "get_existing_user_identifiers_for_write", wrapped)

    register_user("alice", "alice@example.com", "StrongPass123!")

    assert called["ok"] is True


@pytest.mark.django_db
def test_update_user_does_not_use_replica_read_selector(monkeypatch):
    from apps.users.services import user_service

    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="StrongPass123!"
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("replica read selector used in write path")

    monkeypatch.setattr(user_service, "get_existing_user_identifiers", fail_if_called, raising=False)
    monkeypatch.setattr(user_service, "get_user_by_id", fail_if_called, raising=False)

    update_user(user.id, email="new@example.com")


@pytest.mark.django_db
def test_update_user_uses_primary_selectors(monkeypatch):
    from apps.users.services import user_service

    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="StrongPass123!"
    )
    called = {"ok": False, "lookup": False}

    def wrapped(*args, **kwargs):
        called["ok"] = True
        return None

    def lookup_wrapped(*args, **kwargs):
        called["lookup"] = True
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": True,
        }

    monkeypatch.setattr(
        user_service, "get_existing_user_identifiers_for_write_excluding", wrapped
    )
    monkeypatch.setattr(user_service, "get_user_by_id_for_write", lookup_wrapped)

    update_user(user.id, email="new@example.com")

    assert called["ok"] is True
    assert called["lookup"] is True


@pytest.mark.django_db
def test_deactivate_user_does_not_use_replica_selector(monkeypatch):
    from apps.users.services import user_service

    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="StrongPass123!"
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("replica read selector used in write path")

    monkeypatch.setattr(user_service, "get_existing_user_identifiers", fail_if_called, raising=False)
    monkeypatch.setattr(user_service, "get_user_by_id", fail_if_called, raising=False)

    deactivate_user(user.id)


@pytest.mark.django_db
def test_cached_selector_returns_dict_and_blocks_orm_instances():
    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="StrongPass123!"
    )
    dto = get_user_by_id_cached(user.id)
    assert isinstance(dto, dict)
    assert not hasattr(dto, "save")

    cache_key = "users:v1:by-id:%s" % user.id
    cache.set(cache_key, user, timeout=60)
    with pytest.raises(TypeError):
        get_user_by_id_cached(user.id)
