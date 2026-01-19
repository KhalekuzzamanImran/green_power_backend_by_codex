from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


def authenticate_user(username: str, password: str) -> User | None:
    return authenticate(username=username, password=password)


def issue_tokens_for_user(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def refresh_tokens(refresh_token: str) -> dict[str, str]:
    refresh = RefreshToken(refresh_token)
    data = {"access": str(refresh.access_token)}
    if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS"):
        if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION"):
            refresh.blacklist()
        refresh.set_jti()
        refresh.set_exp()
        data["refresh"] = str(refresh)
    return data


def blacklist_refresh_token(refresh_token: str) -> None:
    refresh = RefreshToken(refresh_token)
    refresh.blacklist()
