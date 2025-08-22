from django.db import models
from django.shortcuts import render
from django.http import JsonResponse
from .models import PortfolioItem, Category, Service
from django.core.serializers import serialize
import json

def paginate_queryset(queryset, page, page_size, request):
    """Helper function to paginate queryset and return paginated data"""
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    # Validate and set page and page size limits
    min_page_size = 5
    max_page_size = 200
    default_page_size = 20

    try:
        page_size = int(page_size) if page_size else default_page_size
        page_size = max(min_page_size, min(page_size, max_page_size))
    except (ValueError, TypeError):
        page_size = default_page_size

    # Create paginator
    paginator = Paginator(queryset, page_size)

    try:
        page_number = int(page) if page else 1
        page_obj = paginator.page(page_number)
    except (ValueError, TypeError, EmptyPage):
        page_obj = paginator.page(1)

    # Get items for current page
    items = page_obj.object_list
    
    # Build pagination metadata
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

# GET all portfolio items
def portfolio_list(request):
    """API endpoint to get all portfolio items with pagination"""
    if request.method == 'GET':
        # Get pagination parameters
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)

        # Get all items ordered by upload date
        portfolio_items = PortfolioItem.objects.select_related('category', 'service').order_by('-upload_date')

        # Apply pagination
        items, pagination_data = paginate_queryset(portfolio_items, page, page_size, request)
        
        portfolio_items = PortfolioItem.objects.all().order_by('-upload_date')

        # Serialize items
        data = []
        for item in items:
            data.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'category': item.category.name,
                'category_id': item.category.id,
                'service': item.service.name if item.service else None,
                'service_id': item.service.id if item.service else None,
                'image_url': request.build_absolute_uri(item.image.url) if item.image else None,
                'upload_date': item.upload_date.isoformat(),
            })
        
        return JsonResponse({
            'portfolio_items': data,
            'pagination': pagination_data
        }, safe=False)

# GET a single portfolio item
def portfolio_detail(request, item_id):
    """API endpoint to get a specific portfolio item"""
    if request.method == 'GET':
        try:
            item = PortfolioItem.objects.get(id=item_id)
            data = {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'category': item.category.name,
                'category_id': item.category.id,
                'service': item.service.name if item.service else None,
                'service_id': item.service.id if item.service else None,
                'image_url': request.build_absolute_uri(item.image.url) if item.image else None,
                'upload_date': item.upload_date.isoformat(),
            }

            return JsonResponse(data, safe=False)
        except PortfolioItem.DoesNotExist:
            return JsonResponse({'error': 'Portfolio item not found'}, status=404)

# GET portfolio items by category
def portfolio_by_category(request, category):
    """API endpoint to get portfolio items by category"""
    if request.method == 'GET':
        try:
            category_obj = Category.objects.get(name__iexact=category)
            portfolio_items = PortfolioItem.objects.filter(category=category_obj).order_by('-upload_date')
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)

        data = []
        for item in portfolio_items:
            data.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'category': item.category.name,
                'category_id': item.category.id,
                'service': item.service.name if item.service else None,
                'service_id': item.service.id if item.service else None,
                'image_url': request.build_absolute_uri(item.image.url) if item.image else None,
                'upload_date': item.upload_date.isoformat(),
            })
        
        return JsonResponse({'portfolio_items': data, 'category': category}, safe=False)

def portfolio_search(request):
    """API endpoint to search portfolio items by text"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()

        if not query:
            return JsonResponse({'error': 'Search query is required'}, status=400)
        
        # Search in title and description
        portfolio_items = PortfolioItem.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query)
        ).order_by('-upload_date')

        data = []
        for item in portfolio_items:
            data.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'category': item.category.name,
                'category_id': item.category.id,
                'service': item.service.name if item.service else None,
                'service_id': item.service.id if item.service else None,
                'image_url': request.build_absolute_uri(item.image.url) if item.image else None,
                'upload_date': item.upload_date.isoformat(),
            })
        
        return JsonResponse({
            'search_query': query,
            'results_count': len(data),
            'portfolio_items': data
        }, safe=False)
    
def portfolio_filter(request):
    """API endpoint to filter portfolio items by multiple criteria"""
    if request.method == 'GET':
        # Get filter parameters
        category = request.GET.get('category', '').strip()
        service = request.GET.get('service', '').strip()

        # Start with all items
        portfolio_items = PortfolioItem.objects.all()
        
        # Apply filters
        if category:
            portfolio_items = portfolio_items.filter(category__name__iexact=category)

        if service:
            portfolio_items = portfolio_items.filter(service__name__iexact=service)

        # Order by upload date
        portfolio_items = portfolio_items.order_by('-upload_date')

        data = []
        for item in portfolio_items:
            data.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'category': item.category.name,
                'category_id': item.category.id,
                'service': item.service.name if item.service else None,
                'service_id': item.service.id if item.service else None,
                'image_url': request.build_absolute_uri(item.image.url) if item.image else None,
                'upload_date': item.upload_date.isoformat(),
            })

        return JsonResponse({
            'filters_applied': {
                'category': category if category else None,
                'service': service if service else None,
            },
            'results_count': len(data),
            'portfolio_items': data
        }, safe=False)
    
def portfolio_combined_filter(request):
    """API endpoint for combined search and filtering"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        category = request.GET.get('category', '').strip()
        service = request.GET.get('service', '').strip()

        # Start with all items
        portfolio_items = PortfolioItem.objects.all()

        # Apply text search if query provided
        if query:
            portfolio_items = portfolio_items.filter(
                models.Q(title__icontains=query) |
                models.Q(description__icontains=query)
            )

        # Apply filters
        if category:
            portfolio_items = portfolio_items.filter(category__name__iexact=category)

        if service:
            portfolio_items = portfolio_items.filter(service__name__iexact=service)

        # Order by upload date
        portfolio_items = portfolio_items.order_by('-upload_date')

        data = []
        for item in portfolio_items:
            data.append({
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'category': item.category.name,
                'category_id': item.category.id,
                'service': item.service.name if item.service else None,
                'service_id': item.service.id if item.service else None,
                'image_url': request.build_absolute_uri(item.image.url) if item.image else None,
                'upload_date': item.upload_date.isoformat(),
            })

        return JsonResponse({
            'search_query': query if query else None,
            'filters_applied': {
                'category': category if category else None,
                'service': service if service else None,
            },
            'results_count': len(data),
            'portfolio_items': data
        }, safe=False)