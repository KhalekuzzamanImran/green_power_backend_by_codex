from django.db import migrations, models
import django.db.models.deletion


def create_roles_and_assign(apps, schema_editor):
    Role = apps.get_model("users", "Role")
    User = apps.get_model("users", "User")

    admin_role, _ = Role.objects.get_or_create(key="admin", defaults={"name": "Admin"})
    staff_role, _ = Role.objects.get_or_create(key="staff", defaults={"name": "Staff"})
    user_role, _ = Role.objects.get_or_create(key="user", defaults={"name": "User"})

    for user in User.objects.all():
        if user.is_superuser:
            user.role = admin_role
        elif user.is_staff:
            user.role = staff_role
        else:
            user.role = user_role
        user.save(update_fields=["role"])


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_role_and_user_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="role",
            name="key",
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
        migrations.RunPython(create_roles_and_assign, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="role",
            name="key",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="users.role",
            ),
        ),
    ]
