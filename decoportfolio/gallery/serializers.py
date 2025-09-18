from rest_framework import serializers
from .models import PortfolioItem, Category, Service, BusinessInfo

class BusinessInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessInfo
        fields = [
            'id', 'company_name', 'tagline', 'description', 'email', 
            'phone', 'address', 'years_experience', 'specialties'
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'display_order']

class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'price_range', 'category', 'is_active', 'display_order']

class PortfolioItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    gallery_image_url = serializers.SerializerMethodField()
    before_image_url = serializers.SerializerMethodField()
    after_image_url = serializers.SerializerMethodField()
    before_thumbnail_url = serializers.SerializerMethodField()
    after_thumbnail_url = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    has_before_after = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioItem
        fields = [
            'id', 'title', 'description', 'category', 'service',
            'image_url', 'thumbnail_url', 'gallery_image_url',
            'before_image_url', 'after_image_url', 'before_thumbnail_url', 'after_thumbnail_url',
            'images', 'image_count', 'has_before_after', 'is_before_after', 'upload_date'
        ]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    def get_gallery_image_url(self, obj):
        if obj.gallery_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.gallery_image.url)
            return obj.gallery_image.url
        return None
    
    def get_before_image_url(self, obj):
        if obj.before_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.before_image.url)
            return obj.before_image.url
        return None
    
    def get_after_image_url(self, obj):
        if obj.after_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.after_image.url)
            return obj.after_image.url
        return None

    def get_before_thumbnail_url(self, obj):
        if obj.before_thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.before_thumbnail.url)
            return obj.before_thumbnail.url
        return None

    def get_after_thumbnail_url(self, obj):
        if obj.after_thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.after_thumbnail.url)
            return obj.after_thumbnail.url
        return None
        
    def get_image_count(self, obj):
        return len(obj.images) if obj.images else 0

    def get_has_before_after(self, obj):
        return obj.has_before_after()