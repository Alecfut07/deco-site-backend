from django.contrib import admin
from .models import PortfolioItem, Category, Service

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'display_order']
    list_editable = ['display_order']
    search_fields = ['name', 'description']
    ordering = ['display_order', 'name']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_range', 'is_active', 'display_order']
    list_editable = ['is_active', 'display_order']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['display_order', 'name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing & Display', {
            'fields': ('price_range', 'is_active', 'display_order')
        }),
    )


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'service', 'upload_date', 'image_preview']
    list_filter = ['category', 'service', 'upload_date']
    search_fields = ['title', 'description', 'category__name', 'service__name']
    ordering = ['-upload_date']
    readonly_fields = ['upload_date']

    fieldsets = (
        ('Content', {
            'fields': ('title', 'description', 'image')
        }),
        ('Organization', {
            'fields': ('category', 'service')
        }),
        ('Metadata', {
            'fields': ('upload_date',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />'
        return 'No image'
    
    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True