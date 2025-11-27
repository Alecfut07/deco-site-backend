from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from gallery.models import FamilyMember
import getpass


class Command(BaseCommand):
    help = "Change password for a FamilyMember user"

    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "username",
            help="Username of the FamilyMember user",
        )
        parser.add_argument(
            "--database",
            action="store",
            dest="database",
            default=DEFAULT_DB_ALIAS,
            help="Specifies the database to use. Default is the default.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        database = options["database"]

        try:
            user = FamilyMember.objects.using(database).get(username=username)
        except FamilyMember.DoesNotExist:
            raise CommandError("FamilyMember user '%s' does not exist" % username)

        self.stdout.write("Changing password for FamilyMember user '%s'\n" % username)

        MAX_TRIES = 3
        count = 0
        p1 = p2 = 1

        while p1 != p2 and count < MAX_TRIES:
            p1 = getpass.getpass()
            if len(p1) < 8:
                self.stdout.write(
                    self.style.ERROR(
                        "Error: Password must be at least 8 characters long."
                    )
                )
                count += 1
                continue
            p2 = getpass.getpass("Password (again): ")
            if p1 != p2:
                self.stdout.write(
                    self.style.ERROR("Error: Your passwords didn't match.")
                )
                count += 1
            else:
                break

        if count == MAX_TRIES:
            raise CommandError(
                "Aborting password change for user '%s' after %s attempts"
                % (username, count)
            )

        user.set_password(p1)
        user.save(using=database)

        return "Password changed successfully for FamilyMember user '%s'" % username
