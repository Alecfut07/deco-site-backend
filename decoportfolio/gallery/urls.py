from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('api/gallery/', views.portfolio_list, name='portfolio_list'),
    path('api/gallery/<int:item_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('api/gallery/category/<str:category>/', views.portfolio_by_category, name='portfolio_by_category'),

    # New search and filter endpoints
    path('api/gallery/search/', views.portfolio_search, name='portfolio_search'),
    path('api/gallery/filter/', views.portfolio_filter, name='portfolio_filter'),
    path('api/gallery/combined/', views.portfolio_combined_filter, name='portfolio_combined_filter'),
]