from django.contrib import admin
from django.utils.html import format_html
from .models import PortfolioItem, Category, Service, BusinessInfo, PortfolioImage, PortfolioVideo

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

class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1
    fields = ('image', 'caption', 'display_order', 'created_at')
    readonly_fields = ('created_at')

class PortfolioVideoInline(admin.TabularInline):
    model = PortfolioVideo
    extra = 1
    fields = ('video', 'caption', 'display_order', 'created_at')
    readonly_fields = ('created_at')

@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ['portfolio_item', 'caption', 'display_order', 'created_at']
    list_filter = ['portfolio_item']
    search_fields = ['portfolio_item__title', 'caption']
    ordering = ['display_order', 'created_at']

@admin.register(PortfolioVideo)
class PortfolioVideoAdmin(admin.ModelAdmin):
    list_display = ['portfolio_item', 'caption', 'display_order', 'created_at']
    list_filter = ['portfolio_item']
    search_fields = ['portfolio_item__title', 'caption']
    ordering = ['display_order', 'created_at']

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'service', 'has_main_image', 'has_before_after', 'upload_date', 'image_preview']
    list_filter = ['category', 'service', 'is_before_after', 'upload_date']
    search_fields = ['title', 'description', 'category__name', 'service__name']
    ordering = ['-upload_date']
    readonly_fields = ['upload_date']

    inlines = [
        PortfolioImageInline,
        PortfolioVideoInline,
    ]

    fieldsets = (
        ('Content', {
            'fields': ('title', 'description')
        }),
        ('Main Image', {
            'fields': ('image',),
            'description': 'Upload the main project image. Thumbnails will be generated automatically.'
        }),
        ('Before/After Images', {
            'fields': ('before_image', 'after_image'),
            'description': 'Upload before and after images (optional). Thumbnails will be generated automatically.'
        }),
        ('Additional Images', {
            'fields': ('images',),
            'description': 'Additional image URLs (optional). Use this for extra project photos.'
        }),
        ('Project Details', {
            'fields': ('is_before_after',)
        }),
        ('Organization', {
            'fields': ('category', 'service')
        }),
        ('Metadata', {
            'fields': ('upload_date',)
        }),
    )

    def has_main_image(self, obj):
        return bool(obj.image)
    has_main_image.short_description = 'Has Main Image'
    has_main_image.boolean = True

    def has_before_after(self, obj):
        return obj.has_before_after()
    has_before_after.short_description = 'Before/After'
    has_before_after.boolean = True

    def image_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; object-fit: cover;" />',
                obj.thumbnail.url
            )
        elif obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'
