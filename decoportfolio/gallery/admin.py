from django.contrib import admin
from .models import PortfolioItem, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'display_order']
    list_editable = ['display_order']
    search_fields = ['name', 'description']
    ordering = ['display_order', 'name']

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'upload_date', 'image_preview']
    list_filter = ['category', 'upload_date']
    search_fields = ['title', 'description', 'category__name']
    ordering = ['-upload_date']
    readonly_fields = ['upload_date']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />'
    
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True