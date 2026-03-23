from django.db import models

from apps.core.models import BaseModel


class Client(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

# Create your models here.
