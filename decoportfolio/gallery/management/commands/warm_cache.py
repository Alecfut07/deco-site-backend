import time
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.test import RequestFactory
from gallery.models import PortfolioItem, Category, Service, BusinessInfo
from gallery.serializers import PortfolioItemSerializer, CategorySerializer, ServiceSerializer, BusinessInfoSerializer

class Command(BaseCommand):
    help = 'Warm up the cache with frequently accessed data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing cache before warming'
        )
    
    def handle(self, *args, **options):
        start_time = time.time()
        
        if options['clear']:
            self.stdout.write("Clearing existing cache...")
            cache.clear()

        self.stdout.write("Starting cache warming...")

        # Create a fake request for serializer context
        factory = RequestFactory()
        request = factory.get('/')

        # Warm portfolio items cache
        self.warm_portfolio_cache(request)

        # Warm categories cache
        self.warm_categories_cache(request)

        # Warm services cache
        self.warm_services_cache(request)

        # Warm business info cache
        self.warm_business_cache(request)

        # Warm search/filter caches
        self.warm_search_caches(request)

        end_time = time.time()
        duration = end_time - start_time
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Cache warming completed in {duration:.2f} seconds"
            )
        )
    
    def warm_portfolio_cache(self, request):
        """Warm portfolio items cache"""
        self.stdout.write("Warming portfolio cache...")

        # Main portfolio list
        items = PortfolioItem.objects.select_related('category', 'service').order_by('-upload_date')[:50]
        serializer = PortfolioItemSerializer(items, many=True, context={'request': request})

        cache_data = {
            'portfolio_items': serializer.data,
            'pagination': {
                'page': 1,
                'page_size': 50,
                'total_items': PortfolioItem.objects.count(),
                'total_pages': 1,
                'has_next': False,
                'has_previous': False
            }
        }

        cache.set('portfolio_list_', cache_data, 300)
        self.stdout.write(f"Cached {len(items)} portfolio items")

    def warm_categories_cache(self, request):
        """Warm categories cache"""
        self.stdout.write("Warming categories cache...")

        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        cache.set('categories_list_', serializer.data, 600)

        self.stdout.write(f"Cached {len(categories)} categories")