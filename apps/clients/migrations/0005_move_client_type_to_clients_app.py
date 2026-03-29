import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboards", "0002_normalize_dashboard_models"),
        ("clients", "0004_rename_name_to_site_name_remove_contact_fields"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="ClientType",
                    fields=[
                        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        ("code", models.CharField(max_length=50, unique=True)),
                        ("name", models.CharField(max_length=100, unique=True)),
                        ("is_active", models.BooleanField(default=True)),
                    ],
                    options={"ordering": ["name"], "db_table": "dashboards_clienttype"},
                ),
                migrations.AlterField(
                    model_name="client",
                    name="client_type",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="clients",
                        to="clients.clienttype",
                    ),
                ),
            ],
        ),
    ]
