from django.core.management.base import BaseCommand
from django.db import transaction
from gallery.models import PortfolioItem, Service, Category

class Command(BaseCommand):
    help = 'Clear all gallery data (portfolio items, services, and categories)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to clear all data',
        )

    def handle(self, *args, **kwargs):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL portfolio items, services, and categories!'
                )
            )
            self.stdout.write('Run with --confirm to proceed')
            return
        
        self.stdout.write('Starting to clear gallery data...')

        with transaction.atomic():
            # Delete in proper order (foreign key dependencies)
            PortfolioItem.objects.all().delete()
            self.stdout.write('  Deleted all portfolio items')

            Service.objects.all().delete()
            self.stdout.write('  Deleted all services')

            Category.objects.all().delete()
            self.stdout.write('  Deleted all categories')

        self.stdout.write(
            self.style.SUCCESS('Successfully cleared all gallery data!')
        )