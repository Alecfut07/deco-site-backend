from django.contrib import admin
from .models import PortfolioItem

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'upload_date']
    list_filter = ['category', 'upload_date']
    search_fields = ['title', 'description']
    ordering = ['-upload_date']
    readonly_fields = ['upload_date']