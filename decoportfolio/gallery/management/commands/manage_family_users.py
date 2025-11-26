from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Manage users in the Family group"

    def add_arguments(self, parser):
        parser.add_argument(
            "--add",
            type=str,
            help="Add a user to the Family group (provide username)",
        )
        parser.add_argument(
            "--remove",
            type=str,
            help="Remove a user from the Family group (provide username)",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List all users in the Family group",
        )
        parser.add_argument(
            "--create-user",
            type=str,
            nargs=2,
            metavar=("USERNAME", "EMAIL"),
            help="Create a new user and add to Family group (username, email)",
        )

        def handle(self, *args, **options):
            # Get or create Family group
            family_group, created = Group.objects.get_or_create(name="Family")

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully created Family group")
                )
            else:
                self.stdout.write(f"Family group already exists")

            # Add user to Family group
            if options["add"]:
                username = options["add"]
                try:
                    user = User.objects.get(username=username)
                    family_group.user_set.add(user)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfuly added {username} to Family group"
                        )
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"User {username} does not exist")
                    )

            # Remove user from Family group
            if options["remove"]:
                username = options["remove"]
                try:
                    user = User.objects.get(username=username)
                    family_group.user_set.remove(user)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully removed {username} from Family group"
                        )
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"User {username} does not exist")
                    )

            # List all Family group users
            if options["list"]:
                family_members = family_group.user_set.all()
                if family_members:
                    self.stdout.write(self.style.SUCCESS("\nFamily Group Members:"))
                    for user in family_members:
                        status = " (superuser)" if user.is_superuser else ""
                        self.stdout.write(f"  - {user.username} ({user.email}){status}")
                else:
                    self.stdout.write(self.style.WARNING("No users in Family group"))

            # Create new user and add to Family group
            if options["create_user"]:
                username, email = options["create_user"]
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.ERROR(f"User {username} already exists")
                    )
                else:
                    # Create user (password will need to be set separately)
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password="temp_password_change_me",  # User should change this
                    )
                    family_group.user_set.add(user)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully created user {username} and added to Family group.\n"
                            f"Please set password with: python manage.py changepassword {username}"
                        )
                    )
