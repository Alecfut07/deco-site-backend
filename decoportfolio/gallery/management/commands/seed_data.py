from django.core.management.base import BaseCommand
from django.db import transaction
from gallery.models import Category, Service, PortfolioItem

class Command(BaseCommand):
    help = 'Seed the database with initial data for Ortega Reyes Remodeling and Restoration'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed database...')

        with transaction.atmoic():
            # Create categories
            self.create_categories()

            # Create services
            self.create_services()

            # Create example portfolio items
            # There are just examples
            self.create_portfolio_items()

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database!')
        )
    
    def create_categories(self):
        """Create all categories"""
        self.stdout.write('Creating categories...')

        categories_data = [
            {
                'name': 'Bathrooms',
                'description': 'Bathroom remodeling, renovation, and restoration services',
                'display_order': 1
            },
            {
                'name': 'Kitchens',
                'description': 'Kitchen remodeling, renovation, and restoration services',
                'display_order': 2
            },
            {
                'name': 'Interior',
                'description': 'General interior remodeling and restoration work',
                'display_order': 3
            },
            {
                'name': 'Exterior',
                'description': 'Exterior remodeling, painting, and restoration services',
                'display_order': 4
            }
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  Created category: {category.name}')
            else:
                self.stdout.write(f'  Category already exists: {category.name}')