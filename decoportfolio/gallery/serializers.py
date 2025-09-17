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
    primary_image_url = serializers.SerializerMethodField()
    before_image_url = serializers.SerializerMethodField()
    after_image_url = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    has_before_after = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioItem
        fields = [
            'id', 'title', 'description', 'category', 'service',
            'images', 'primary_image_url', 'image_count',
            'before_image_url', 'after_image_url', 'has_before_after',
            'is_before_after', 'upload_date'
        ]

    def get_primary_image_url(self, obj):
        primary_image = obj.get_primary_image()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image)
            return primary_image
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
        
    def get_image_count(self, obj):
        return len(obj.images) if obj.images else 0

    def get_has_before_after(self, obj):
        return obj.has_before_after()