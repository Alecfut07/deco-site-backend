from django.contrib import admin
from django.utils.html import format_html
from .models import PortfolioItem, Category, Service, BusinessInfo

@admin.register(BusinessInfo)
class BusinessInfoAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'phone', 'years_experience', 'is_active']
    list_editable = ['is_active']
    search_fields = ['company_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'tagline', 'description')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Business Details', {
            'fields': ('years_experience', 'specialties')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

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
    list_display = ['title', 'category', 'service', 'image_count', 'has_before_after', 'upload_date', 'image_preview']
    list_filter = ['category', 'service', 'is_before_after', 'upload_date']
    search_fields = ['title', 'description', 'category__name', 'service__name']
    ordering = ['-upload_date']
    readonly_fields = ['upload_date']

    fieldsets = (
        ('Content', {
            'fields': ('title', 'description')
        }),
        ('Images', {
            'fields': ('images', 'before_image', 'after_image'),
            'description': 'Upload multiple images for the main portfolio. Before/After images are optional.'
        }),
        ('Organization', {
            'fields': ('category', 'service')
        }),
        ('Metadata', {
            'fields': ('upload_date',)
        }),
    )

    def image_count(self, obj):
        return len(obj.images) if obj.images else 0
    image_count.short_description = 'Image Count'

    def has_before_after(self, obj):
        return obj.has_before_after()
    has_before_after.short_description = 'Before/After'
    has_before_after.boolean = True

    def image_preview(self, obj):
        primary_image = obj.get_primary_image()
        if primary_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; object-fit: cover;" />',
                primary_image
            )
        return "No image"
    image_preview.short_description = 'Primary Image'