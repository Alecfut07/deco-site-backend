from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import PortfolioItem, Category, Service
from .serializers import PortfolioItemSerializer, CategorySerializer, ServiceSerializer

def paginate_queryset(queryset, page, page_size, request):
    """Helper function to paginate queryset and return paginated data"""
    min_page_size = 5
    max_page_size = 200
    default_page = 1
    default_page_size = 20

    try:
        page_size = int(page_size) if page_size else default_page_size
        page_size = max(min_page_size, min(page_size, max_page_size))
    except (ValueError, TypeError):
        page_size = default_page_size

    paginator = Paginator(queryset, page_size)

    try:
        page_number = int(page) if page else default_page
        page_obj = paginator.page(page_number)
    except (ValueError, TypeError, EmptyPage):
        page_obj = paginator.page(default_page)

    items = page_obj.object_list
    
    pagination_data = {
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'page_size': page_size,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
    }

    return items, pagination_data

class PortfolioItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for portfolio items with search, filter, and pagination capabilities

    Provides:
    - List all portfolio items
    - Retrieve individual portfolio items
    - Search by text
    - Filter by category and service
    - Combined search and filtering
    - Pagination support
    """
    queryset = PortfolioItem.objects.select_related('category', 'service').order_by('-upload_date')
    serializer_class = PortfolioItemSerializer
    default_page = 1
    default_page_size = 20

    def portfolio_list(self, request):
        """List all portfolio items with pagination"""
        page = request.GET.get('page', self.default_page)
        page_size = request.GET.get('page_size', self.default_page_size)

        items, pagination_data = paginate_queryset(self.queryset, page, page_size, request)
        serializer = self.get_seiralizer(items, many=True)

        return Response({
            'portfolio_items': serializer.data,
            'pagination': pagination_data
        })
    
    @action(detail=False, methods=['get'])
    def portfolio_search(self, request):
        """"Search portfolio items by text"""
        query = request.GET.get('q', '').strip()
        page = request.GET.get('page', self.default_page)
        page_size = request.GET.get('page_size', self.default_page_size)

        if not query:
            return Response({'error': 'Seach query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in title and description
        search_results = self.queryset.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query)
        )

        items, pagination_data = paginate_queryset(search_results, page, page_size, request)
        serializer = self.get_serializer(items, many=True)

        return Response({
            'search_query': query,
            'portfolio_items': serializer.data,
            'pagination': pagination_data
        })
    
    @action(detail=False, methods=['get'])
    def portfolio_filter(self, request):
        """Filter portfolio items by category and service"""
        category = request.GET.get('category', '').strip()
        service = request.GET.get('service', '').strip()
        page = request.GET.get('page', self.default_page)
        page_size = request.GET.get('page_size', self.default_page_size)

        # Start with all items
        filtered_results = self.queryset.all()

        # Apply filters
        if category:
            filtered_results = filtered_results.filter(category__name__iexact=category)
        
        if service:
            filtered_results = filtered_results.filter(service__name__iexact=service)

        items, pagination_data = paginate_queryset(filtered_results, page, page_size, request)
        serializer = self.get_serializer(items, many=True)

        return Response({
            'filters_applied': {
                'category': category if category else None,
                'service': service if service else None
            },
            'portfolio_items': serializer.data,
            'pagination': pagination_data
        })
    
    @action(detail=False, methods=['get'])
    def portfolio_combined(self, request):
        """Combined search and filtering"""
        query = request.GET.get('q', '').strip()
        category = request.GET.get('category', '').strip()
        service = request.GET.get('service', '').strip()
        page = request.GET.get('page', self.default_page)
        page_size = request.GET.get('page_size', self.default_page_size)

        # Start with all items
        combined_results = self.queryset.all()

        # Apply text search if query provided
        if query:
            combined_results = combined_results.filter(
                models.Q(title__icontains=query) |
                models.Q(description__icontains=query)
            )
        
        # Apply filters
        if category:
            combined_results = combined_results.filter(category__name__iexact=category)

        if service:
            combined_results = combined_results.filter(service__name__iexact=service)

        items, pagination_data = paginate_queryset(combined_results, page, page_size, request)
        serializer = self.get_serializer(items, many=True)

        return Response({
            'search_query': query if query else None,
            'filters_applied': {
                'category': category if category else None,
                'service': service if service else None
            },
            'portfolio_items': serializer.data,
            'pagination': pagination_data
        })