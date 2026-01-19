from django.core.cache import cache
from django.db.models import Q

from apps.users.cache import CACHE_TTL_SECONDS, UserReadDTO, user_cache_key
from apps.users.models import User
from common.db_router import get_primary_db, get_read_db


def get_active_users() -> list[UserReadDTO]:
    """Read path selector: returns DTOs only."""
    return list(
        User.objects.using(get_read_db())
        .filter(is_active=True)
        .values("id", "username", "email", "is_active")
    )


def get_existing_user_identifiers(username: str, email: str) -> tuple[str, str] | None:
    """Read path selector: safe for replica reads."""
    return (
        User.objects.using(get_read_db())
        .filter(Q(username__iexact=username) | Q(email__iexact=email))
        .values_list("username", "email")
        .first()
    )


def get_existing_user_identifiers_for_write(username: str, email: str) -> tuple[str, str] | None:
    # Use primary to avoid replica lag during write-adjacent checks.
    return (
        User.objects.using(get_primary_db())
        .filter(Q(username__iexact=username) | Q(email__iexact=email))
        .values_list("username", "email")
        .first()
    )


def get_existing_user_identifiers_for_write_excluding(
    user_id: int, username: str, email: str
) -> tuple[str, str] | None:
    return (
        User.objects.using(get_primary_db())
        .exclude(id=user_id)
        .filter(Q(username__iexact=username) | Q(email__iexact=email))
        .values_list("username", "email")
        .first()
    )


def get_user_by_id_cached(user_id: int) -> UserReadDTO | None:
    """Cached selector: returns immutable DTO, never ORM instances."""
    cache_key = user_cache_key(user_id)
    cached = cache.get(cache_key)
    if cached is not None:
        if isinstance(cached, User):
            raise TypeError("cached selector returned ORM instance")
        if not isinstance(cached, dict):
            raise TypeError("cached selector returned non-dict payload")
        return cached
    user = get_user_by_id(user_id)
    if user is not None:
        cache.set(cache_key, user, timeout=CACHE_TTL_SECONDS)
        return user
    return None


def get_user_by_id(user_id: int) -> UserReadDTO | None:
    """Read selector: returns DTO only."""
    return (
        User.objects.using(get_read_db())
        .filter(id=user_id, is_active=True)
        .values("id", "username", "email", "is_active")
        .first()
    )


def get_user_by_id_for_write(user_id: int) -> UserReadDTO | None:
    """Write-adjacent selector: returns DTO only, uses primary."""
    return (
        User.objects.using(get_primary_db())
        .filter(id=user_id, is_active=True)
        .values("id", "username", "email", "is_active")
        .first()
    )
