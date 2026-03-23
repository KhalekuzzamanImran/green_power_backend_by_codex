from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import RoleChoices, User


class Command(BaseCommand):
    help = "Create or update a superuser with the ADMIN role."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--first-name", default="")
        parser.add_argument("--last-name", default="")
        parser.add_argument("--phone", default="")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        if not username.strip():
            raise CommandError("Username is required.")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": RoleChoices.ADMIN,
                "first_name": options["first_name"],
                "last_name": options["last_name"],
                "phone": options["phone"],
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if not created:
            user.email = email
            user.role = RoleChoices.ADMIN
            user.first_name = options["first_name"]
            user.last_name = options["last_name"]
            user.phone = options["phone"]
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True

        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} ADMIN superuser: {user.username}"))
