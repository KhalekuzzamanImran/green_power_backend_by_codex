from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError

from apps.users.cache import UserReadDTO, invalidate_user_cache
from apps.users.models import User
from apps.users.repositories.user_repository import create_user, update_user_by_id
from apps.users.selectors.user_selector import (
    get_existing_user_identifiers_for_write,
    get_existing_user_identifiers_for_write_excluding,
    get_user_by_id_for_write,
)
from common.exceptions import UserAlreadyExistsError


def deactivate_user(user_id: int) -> UserReadDTO | None:
    update_user_by_id(user_id, is_active=False)
    invalidate_user_cache(user_id)
    return get_user_by_id_for_write(user_id)


def register_user(username: str, email: str, password: str) -> User:
    existing = get_existing_user_identifiers_for_write(username=username, email=email)
    if existing:
        raise UserAlreadyExistsError("username or email already exists")
    validate_password(password)
    try:
        user = create_user(username=username, email=email, password=password)
    except IntegrityError as exc:
        raise UserAlreadyExistsError("username or email already exists") from exc
    invalidate_user_cache(user.id)
    return user


def update_user(user_id: int, username: str | None = None, email: str | None = None) -> UserReadDTO | None:
    user = get_user_by_id_for_write(user_id)
    if user is None:
        raise ValueError("user not found")
    new_username = username if username is not None else user["username"]
    new_email = email if email is not None else user["email"]
    existing = get_existing_user_identifiers_for_write_excluding(
        user_id=user["id"], username=new_username, email=new_email
    )
    if existing:
        raise UserAlreadyExistsError("username or email already exists")
    update_user_by_id(user_id, username=new_username, email=new_email)
    invalidate_user_cache(user_id)
    return get_user_by_id_for_write(user_id)
