from django.shortcuts import render
from django.http import JsonResponse
from .models import PortfolioItem, Category, Service
from django.core.serializers import serialize
import json

# GET all portfolio items
def portfolio_list(request):
    """API endpoint to get all portfolio items"""
    if request.method == 'GET': 
        portfolio_items = PortfolioItem.objects.all().order_by('-upload_date')

        # Convert to JSON-serializable format
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
        
        return JsonResponse({'portfolio_items': data}, safe=False)

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