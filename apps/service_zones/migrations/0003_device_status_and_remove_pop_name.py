from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service_zones", "0002_device"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="device",
            name="pop_name",
        ),
        migrations.AlterField(
            model_name="device",
            name="status",
            field=models.CharField(
                choices=[("critical", "Critical"), ("major", "Major"), ("minor", "Minor")],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="servicezone",
            name="status",
            field=models.CharField(
                choices=[("critical", "Critical"), ("major", "Major"), ("minor", "Minor")],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="servicezone",
            name="network_status",
            field=models.CharField(
                choices=[("online", "Online"), ("offline", "Offline"), ("warning", "Warning")],
                max_length=30,
            ),
        ),
    ]
