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