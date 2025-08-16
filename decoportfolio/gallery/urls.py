from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('api/gallery/', views.portfolio_list, name='portfolio_list'),
    path('api/gallery/<int:item_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('api/gallery/category/<str:category>/', views.portfolio_by_category, name='portfolio_by_category'),
]