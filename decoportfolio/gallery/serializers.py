from rest_framework import serializers
from .models import PortfolioItem, Category, Service

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

    class Meta:
        model = PortfolioItem
        fields = ['id', 'title', 'description', 'category', 'service', 'image_url', 'upload_date']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None