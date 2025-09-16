from django.core.management.base import BaseCommand
from django.db import transaction
from gallery.models import Category, Service, PortfolioItem, BusinessInfo

class Command(BaseCommand):
    help = 'Seed the database with initial data for Ortega Reyes Remodeling and Restoration'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to seed database...')

        with transaction.atomic():
            # Create business information
            self.create_business_info()
            
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

    def create_business_info(self):
        """Create Business Information"""
        self.stdout.write("Creating Business Information...")

        business_data = {
            'company_name': 'Ortega Reyes Remodeling and Restoration',
            'tagline': '25 Years of Professional Remodeling and Restoration',
            'description': "Professional remodeling and restoration services specializing in bathrooms and kitchens. With over 25 years of experience, we deliver quality workmanship and exceptional customer service.",
            'email': 'alo_57@live.com',
            'phone': '(720) 434-3254',
            'address': 'Serving at Denver, CO',
            'years_experience': 25,
            'specialties': 'Bathrooms, Kitchens, Interior Painting, Exterior Painting, Tiling, Flooring, Drywall, Plumbing',
            'is_active': True
        }

        business_info, created = BusinessInfo.objects.get_or_create(
            company_name=business_data['company_name'],
            defaults=business_data
        )

        if created:
            self.stdout.write(f'  Created business info: {business_info.company_name}')
        else:
            # Update existing business info
            for key, value in business_data.items():
                setattr(business_info, key, value)
            business_info.save()
            self.stdout.write(f'  Updated business info: {business_info.company_name}')
    
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

    def create_portfolio_items(self):
        """Create example portfolio items"""
        self.stdout.write('Creating portfolio items...')

        # Get categories
        bathrooms_cat = Category.objects.get(name='Bathrooms')
        kitchens_cat = Category.objects.get(name='Kitchens')
        interior_cat = Category.objects.get(name='Interior')
        exterior_cat = Category.objects.get(name='Exterior')

        # Get services
        shower_service = Service.objects.get(name='Shower Installation/Renovation')
        tiling_kitchens_service = Service.objects.get(name='Tiling (Kitchens)')
        interior_painting_service = Service.objects.get(name='Interior Painting')
        exterior_painting_service = Service.objects.get(name='Exterior Painting')

        portfolio_items_data = [
            {
                'title': 'Bathroom Renovation Example',
                'description': 'Complete bathroom renovation with new shower, tiling, and plumbing work',
                'category': bathrooms_cat,
                'service': shower_service
            },
            {
                'title': 'Kitchen Remodeling Example',
                'description': 'Kitchen renovation with new flooring, tiling, and painting',
                'category': kitchens_cat,
                'service': tiling_kitchens_service
            },
            {
                'title': 'Interior Painting Example',
                'description': 'Professional interior painting services for living room',
                'category': interior_cat,
                'service': interior_painting_service
            },
            {
                'title': 'Exterior Painting Example',
                'description': 'Exterior house painting and restoration work',
                'category': exterior_cat,
                'service': exterior_painting_service
            }
        ]

        for item_data in portfolio_items_data:
            # Note: You'll need to add an image file for these items
            # For now, we'll create them without images
            portfolio_item, created = PortfolioItem.objects.get_or_create(
                title=item_data['title'],
                defaults=item_data
            )
            if created:
                self.stdout.write(f'  Created portfolio item: {portfolio_item.title}')
            else:
                self.stdout.write(f'  Portfolio item already exists: {portfolio_item.title}')