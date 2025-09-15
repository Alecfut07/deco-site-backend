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

    def create_services(self):
        """Create all services"""
        self.stdout.write('Creating services...')

        services_data = [
            {
                'name': 'Interior Painting',
                'description': 'Professional interior painting services for walls, ceilings, and trim work',
                'price_range': 'Contact for quote',
                'category_name': 'Interior',
                'is_active': True,
                'display_order': 1
            },
            {
                'name': 'Shower Installation/Renovation',
                'description': 'Complete shower installation, renovation, and restoration services',
                'price_range': 'Contact for quote',
                'category_name': 'Bathrooms',
                'is_active': True,
                'display_order': 2
            },
            {
                'name': 'Exterior Painting',
                'description': 'Professional exterior painting and restoration services',
                'price_range': 'Contact for quote',
                'category_name': 'Exterior',
                'is_active': True,
                'display_order': 3
            },
            {
                'name': 'Tiling (Bathrooms)',
                'description': 'Professional tile installation for floors, walls, and backsplashes.',
                'price_range': 'Contact for quote',
                'category_name': 'Bathrooms',
                'is_active': True,
                'display_order': 4
            },
            {
                'name': 'Tiling (Kitchens)',
                'description': 'Professional tile installation for floors, walls, and backsplashes.',
                'price_range': 'Contact for quote',
                'category_name': 'Kitchens',
                'is_active': True,
                'display_order': 5
            },
            {
                'name': 'Hardwood Flooring Installation',
                'description': 'Professional hardwood flooring installation and restoration',
                'price_range': 'Contact for quote',
                'category_name': 'Interior',
                'is_active': True,
                'display_order': 6
            },
            {
                'name': 'Vinyl Flooring Installation',
                'description': 'Professional vinyl flooring installation and restoration',
                'price_range': 'Contact for quote',
                'category_name': 'Interior',
                'is_active': True,
                'display_order': 7
            },
            {
                'name': 'Drywall Finishing',
                'description': 'Professional drywall installation, finishing, and repair services',
                'price_range': 'Contact for quote',
                'category_name': 'Interior',
                'is_active': True,
                'display_order': 8
            },
            {
                'name': 'Plumbing',
                'description': 'Professional plumbing installation, repair, and maintenance services',
                'price_range': 'Contact for quote',
                'category_name': 'Bathrooms',
                'is_active': True,
                'display_order': 9
            }
        ]

        for service_data in services_data:
            category = Category.objects.get(name=service_data['category_name'])
            service_data['category'] = category
            del service_data['category_name']

            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'  Created service: {service.name}')
            else:
                self.stdout.write(f'  Service already exists: {service.name}')