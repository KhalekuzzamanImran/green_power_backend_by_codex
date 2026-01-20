from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("service_zones", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Device",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="device_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="device_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("pop_name", models.CharField(max_length=150)),
                ("device_name", models.CharField(max_length=150)),
                ("device_code", models.CharField(max_length=50, unique=True)),
                ("status", models.CharField(max_length=30)),
                ("remark", models.TextField(blank=True)),
                ("physical_details", models.TextField(blank=True)),
                (
                    "service_zone",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="devices",
                        to="service_zones.servicezone",
                    ),
                ),
            ],
            options={
                "db_table": "devices",
            },
        ),
    ]
