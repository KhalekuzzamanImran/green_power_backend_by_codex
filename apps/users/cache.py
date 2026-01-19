from typing import TypedDict

from apps.users.models import User

CACHE_VERSION = 1
CACHE_TTL_SECONDS = 60


class UserReadDTO(TypedDict):
    id: int
    username: str
    email: str
    is_active: bool


def user_cache_key(user_id: int) -> str:
    return f"users:v{CACHE_VERSION}:by-id:{user_id}"


def serialize_user(user: User) -> UserReadDTO:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
    }


def invalidate_user_cache(user_id: int) -> None:
    from django.core.cache import cache

    cache.delete(user_cache_key(user_id))
