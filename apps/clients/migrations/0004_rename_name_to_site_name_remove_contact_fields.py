from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0003_add_dashboard_scope"),
    ]

    operations = [
        migrations.RenameField(
            model_name="client",
            old_name="name",
            new_name="site_name",
        ),
        migrations.RemoveField(
            model_name="client",
            name="contact_person",
        ),
        migrations.RemoveField(
            model_name="client",
            name="email",
        ),
        migrations.RemoveField(
            model_name="client",
            name="phone",
        ),
        migrations.AlterField(
            model_name="client",
            name="site_name",
            field=models.CharField(max_length=255, verbose_name="Company / Site Name"),
        ),
        migrations.AlterModelOptions(
            name="client",
            options={"ordering": ["site_name"]},
        ),
    ]
