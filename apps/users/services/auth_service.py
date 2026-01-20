from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from common.exceptions import InvalidTokenError


def authenticate_user(username: str, password: str) -> User | None:
    return authenticate(username=username, password=password)


def _get_user_roles(user: User) -> list[str]:
    roles = {"user"}
    roles.update(user.groups.values_list("name", flat=True))
    if user.role:
        roles.add(user.role.key)
    if user.is_staff:
        roles.add("staff")
    if user.is_superuser:
        roles.add("admin")
    if "Staff" in roles:
        roles.add("staff")
    if "Admin" in roles:
        roles.add("admin")
    return sorted(roles)


def issue_tokens_for_user(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    roles = _get_user_roles(user)
    refresh["roles"] = roles
    access = refresh.access_token
    access["roles"] = roles
    return {
        "access": str(access),
        "refresh": str(refresh),
    }


def refresh_tokens(refresh_token: str) -> dict[str, str]:
    try:
        refresh = RefreshToken(refresh_token)
    except TokenError as exc:
        raise InvalidTokenError("invalid or expired refresh token") from exc
    roles = refresh.get("roles") or []
    if not roles:
        user_id = refresh.get("user_id")
        if user_id:
            user = User.objects.filter(id=user_id).first()
            if user:
                roles = _get_user_roles(user)
    if not roles:
        roles = ["user"]
    access = refresh.access_token
    access["roles"] = roles
    data = {"access": str(access)}
    if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS"):
        if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION"):
            try:
                refresh.blacklist()
            except TokenError as exc:
                raise InvalidTokenError("invalid or expired refresh token") from exc
        refresh.set_jti()
        refresh.set_exp()
        refresh["roles"] = roles
        data["refresh"] = str(refresh)
    return data


def blacklist_refresh_token(refresh_token: str) -> None:
    try:
        refresh = RefreshToken(refresh_token)
        refresh.blacklist()
    except TokenError as exc:
        raise InvalidTokenError("invalid or expired refresh token") from exc
