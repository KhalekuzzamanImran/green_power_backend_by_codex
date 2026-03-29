import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0005_move_client_type_to_clients_app"),
        ("dashboards", "0002_normalize_dashboard_models"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="dashboard",
                    name="client_type",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="dashboards",
                        to="clients.clienttype",
                    ),
                ),
                migrations.DeleteModel(
                    name="ClientType",
                ),
            ],
        ),
    ]
