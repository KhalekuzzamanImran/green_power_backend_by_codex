import pytest
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User
from apps.users.services.auth_service import issue_tokens_for_user


@pytest.mark.django_db
def test_issue_tokens_includes_user_role_for_authenticated_user():
    user = User.objects.create_user(username="alice", email="alice@example.com", password="StrongPass123!")

    tokens = issue_tokens_for_user(user)
    access = AccessToken(tokens["access"])

    assert "roles" in access
    assert "user" in access["roles"]


@pytest.mark.django_db
def test_issue_tokens_includes_staff_and_admin_roles():
    staff_group = Group.objects.create(name="Staff")
    admin_group = Group.objects.create(name="Admin")
    user = User.objects.create_user(
        username="alice", email="alice@example.com", password="StrongPass123!", is_staff=True, is_superuser=True
    )
    user.groups.add(staff_group, admin_group)

    tokens = issue_tokens_for_user(user)
    access = AccessToken(tokens["access"])

    assert "staff" in access["roles"]
    assert "admin" in access["roles"]
