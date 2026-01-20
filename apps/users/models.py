from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from common.models import AuditModel

class Role(AuditModel):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "roles"

    def __str__(self) -> str:
        return self.name


class RoleAdminProxy(Role):
    class Meta:
        proxy = True
        app_label = "auth"
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class CustomUserManager(UserManager):
    def _get_or_create_role(self, key: str, name: str) -> Role:
        role, _ = Role.objects.get_or_create(key=key, defaults={"name": name})
        if role.name != name:
            role.name = name
            role.save(update_fields=["name"])
        return role

    def create_user(self, username, email=None, password=None, **extra_fields):
        if "role" not in extra_fields or extra_fields["role"] is None:
            extra_fields["role"] = self._get_or_create_role("user", "User")
        return super().create_user(username, email=email, password=password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields["role"] = self._get_or_create_role("admin", "Admin")
        return super().create_superuser(username, email=email, password=password, **extra_fields)


class User(AbstractUser, AuditModel):
    email = models.EmailField(unique=True, db_index=True)
    role = models.ForeignKey("Role", on_delete=models.PROTECT, related_name="users")

    class Meta:
        db_table = "users"

    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()
