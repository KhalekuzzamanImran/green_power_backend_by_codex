from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["role", "is_active"], name="user_role_active_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["first_name"], name="user_first_name_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["last_name"], name="user_last_name_idx"),
        ),
    ]
