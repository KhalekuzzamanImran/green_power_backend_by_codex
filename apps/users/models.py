from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)

    class Meta:
        db_table = "users"

    is_active = models.BooleanField(default=True)
