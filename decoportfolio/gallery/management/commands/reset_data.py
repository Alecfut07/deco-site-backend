from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Reset all gallery data (clear + seed)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to reset all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALl gallery data and recreate it!'
                )
            )
            self.stdout.write('Run with --confirm to proceed')
            return
        
        self.stdout.write('Starting to reset gallery data...')

        # Clear all data
        call_command('clear_data', confirm=True)

        # Seed fresh data
        call_command('seed_data')

        self.stdout.write(
            self.style.SUCCESS('Successfully reset all gallery data!')
        )