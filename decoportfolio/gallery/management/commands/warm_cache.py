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

    def warm_services_cache(self, request):
        """Warm services cache"""
        self.stdout.write("Warming services cache...")

        services = Service.objects.select_related('category').filter(is_active=True)
        serializer = ServiceSerializer(services, many=True)
        cache.set('services_list_', serializer.data, 600)

        self.stdout.write(f"Cached {len(services)} services")

    def warm_business_cache(self, request):
        """Warm business info cache"""
        self.stdout.write("Warming business info cache...")

        business_info = BusinessInfo.objects.filter(is_active=True).first()
        if business_info:
            serializer = BusinessInfoSerializer(business_info)
            cache.set('business_info_', serializer.data, 1800) # 30 minutes
            self.stdout.write("Cached business info")
    
    def warm_search_caches(self, request):
        """Warm common search/filter caches"""
        self.stdout.write("Warming search/filter caches...")

        # Common search terms
        common_searches = ['interior', 'exterior', 'painting', 'bathroom', 'kitchen']

        for term in common_searches:
            items = PortfolioItem.objects.filter(
                title__icontains=term
            ).select_related('category', 'service')[:20]

            if items:
                serializer = PortfolioItemSerializer(items, many=True, context={'request': request})
                cache_key = f'portfolio_search_{term}_'
                cache.set(cache_key, {
                    'portfolio_items': serializer.data,
                    'search_term': term,
                    'total_results': len(items)
                }, 300)
                self.stdout.write(f"Cached search for '{term}' ({len(items)} results)")