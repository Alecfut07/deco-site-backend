from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import PortfolioItemViewSet, CategoryViewSet, ServiceViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'portfolio-items', PortfolioItemViewSet, basename='portfolioitem')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'services', ServiceViewSet, basename='service')

app_name = 'gallery'

urlpatterns = [
    # Include the router URLs
    path('api/', include(router.urls)),

    # Keep your existing endpoints for backward compatibility
    path('api/gallery/', PortfolioItemViewSet.as_view({'get': 'list'}), name='portfolio_list'),
    path('api/gallery/<int:pk>/', PortfolioItemViewSet.as_view({'get': 'retrieve'}), name='portfolio_detail'),
    path('api/gallery/search/', PortfolioItemViewSet.as_view({'get': 'search'}), name='portfolio_search'),
    path('api/gallery/filter/', PortfolioItemViewSet.as_view({'get': 'filter'}), name='portfolio_filter'),
    path('api/gallery/combined/', PortfolioItemViewSet.as_view({'get': 'combined'}), name='portfolio_combined'),
    path('api/gallery/category/<str:category>/', PortfolioItemViewSet.as_view({'get': 'by_category'}), name='portfolio_by_category'),
]