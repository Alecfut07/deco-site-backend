from django.core.management.base import BaseCommand
from gallery.models import FamilyMember


class Command(BaseCommand):
    help = "Manage FamilyMember users (separate from Django Admin users)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--list",
            action="store_true",
            help="List all FamilyMember users",
        )
        parser.add_argument(
            "--create-user",
            type=str,
            nargs=2,
            metavar=("USERNAME", "EMAIL"),
            help="Create a new FamilyMember user",
        )
        parser.add_argument(
            "--add",
            type=str,
            metavar="USERNAME",
            help="Add existing FamilyMember user (no-op, users are automatically family members)",
        )
        parser.add_argument(
            "--remove",
            type=str,
            metavar="USERNAME",
            help="Deactivate a FamilyMember user",
        )
        parser.add_argument(
            "--activate",
            type=str,
            metavar="USERNAME",
            help="Activate a FamilyMember user",
        )

    def handle(self, *args, **options):
        if options["list"]:
            self.list_users()
        elif options["create_user"]:
            username, email = options["create_user"]
            self.create_user(username, email)
        elif options["add"]:
            self.stdout.write(
                self.style.WARNING(
                    "All FamilyMember users are automatically family members. "
                    "Use --activate to activate a user."
                )
            )
        elif options["remove"]:
            self.deactivate_user(options["remove"])
        elif options["activate"]:
            self.activate_user(options["activate"])
        else:
            self.stdout.write(
                self.style.ERROR("Please specify an action. Use --help for options.")
            )

    def list_users(self):
        users = FamilyMember.objects.all().order_by("username")
        if users.exists():
            self.stdout.write(
                self.style.SUCCESS(f"\nFound {users.count()} FamilyMember user(s):\n")
            )
            for user in users:
                status = "Active" if user.is_active else "Inactive"
                self.stdout.write(f"  - {user.username} ({user.email}) - {status}")
        else:
            self.stdout.write(self.style.WARNING("No FamilyMember users found."))

    def create_user(self, username, email):
        if FamilyMember.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f"FamilyMember user {username} already exists.")
            )
            return

        if FamilyMember.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Email {email} is already in use"))
            return

        user = FamilyMember.objects.create_user(
            username=username,
            email=email,
            password="temp_password_change_me",  # User should change this
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created FamilyMember user {username}.\n"
                f"Please set password with: python manage.py changepassword {username}"
            )
        )

    def deactivate_user(self, username):
        try:
            user = FamilyMember.objects.get(username=username)
            user.is_active = False
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deactivated FamilyMember user {username}"
                )
            )
        except FamilyMember.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"FamilyMember user {username} does not exist")
            )

    def activate_user(self, username):
        try:
            user = FamilyMember.objects.get(username=username)
            user.is_active = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully activated FamilyMember user {username}"
                )
            )
        except FamilyMember.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"FamilyMember user {username} does not exist")
            )
