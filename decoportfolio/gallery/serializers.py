from rest_framework import serializers
from django.conf import settings
import os
from .models import (
    PortfolioItem,
    Category,
    Service,
    BusinessInfo,
    PortfolioImage,
    PortfolioVideo,
)


class FamilyLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "passowrd"})


class BusinessInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessInfo
        fields = [
            "id",
            "company_name",
            "tagline",
            "description",
            "email",
            "phone",
            "address",
            "years_experience",
            "specialties",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "display_order"]


class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Service
        fields = ["id", "name", "category", "price_range", "is_active", "display_order"]


class PortfolioImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    gallery_image_url = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioImage
        fields = [
            "id",
            "portfolio_item",
            "image",
            "image_url",
            "thumbnail_url",
            "gallery_image_url",
            "caption",
            "display_order",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "image_url",
            "thumbnail_url",
            "gallery_image_url",
            "created_at",
        ]
        # Prevent image from being included in the API response
        # Your frontend will handle the image display (image_url, thumbnail_url, etc).
        extra_kwargs = {
            "image": {"write_only": True},
        }

    def _build_url(self, request, path):
        if request:
            return request.build_absolute_uri(path)
        return path

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            return self._build_url(request, obj.image.url)
        return None

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get("request")
            return self._build_url(request, obj.thumbnail.url)
        return None

    def get_gallery_image_url(self, obj):
        if obj.gallery_image:
            request = self.context.get("request")
            return self._build_url(request, obj.gallery_image.url)


class PortfolioVideoSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioVideo
        fields = [
            "id",
            "portfolio_item",
            "video",
            "video_url",
            "thumbnail_url",
            "caption",
            "display_order",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "video_url",
            "thumbnail_url",
            "created_at",
        ]
        # Prevent video from being included in the API response
        # Your frontend will handle the video display (video_url, etc).
        extra_kwargs = {
            "video": {"write_only": True},
        }

    def get_video_url(self, obj):
        if obj.video:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None


class PortfolioItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    pictures = PortfolioImageSerializer(many=True, read_only=True)
    videos = PortfolioVideoSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    gallery_image_url = serializers.SerializerMethodField()
    before_image_url = serializers.SerializerMethodField()
    after_image_url = serializers.SerializerMethodField()
    before_thumbnail_url = serializers.SerializerMethodField()
    after_thumbnail_url = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    has_before_after = serializers.SerializerMethodField()

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source="service",
        write_only=True,
        required=False,
    )

    class Meta:
        model = PortfolioItem
        fields = [
            "id",
            "title",
            "description",
            "category",
            "service",
            "category_id",
            "service_id",
            "image",
            "image_url",
            "thumbnail_url",
            "gallery_image_url",
            "before_image",
            "after_image",
            "before_image_url",
            "after_image_url",
            "before_thumbnail_url",
            "after_thumbnail_url",
            "pictures",
            "videos",
            "image_count",
            "has_before_after",
            "is_before_after",
            "upload_date",
        ]
        read_only_fields = [
            "id",
            "image_url",
            "thumbnail_url",
            "gallery_image_url",
            "before_image_url",
            "after_image_url",
            "before_thumbnail_url",
            "after_thumbnail_url",
            "pictures",
            "videos",
            "image_count",
            "has_before_after",
            "upload_date",
        ]
        extra_kwargs = {
            "image": {"required": False},
            "before_image": {"required": False},
            "after_image": {"required": False},
        }

    def validate(self, data):
        """
        Validate that portfolio item has at least one image or video.
        This ensures that items with only videos can be created.
        """

        # Check if this is an update (self.instance exists)
        if self.instance:
            # For updates, check existing data + new data
            has_main_image = data.get("image") or self.instance.image
            has_before = data.get("before_image") or self.instance.before_image
            has_after = data.get("after_image") or self.instance.after_image
            has_gallery_images = self.instance.pictures.exists()
            has_videos = self.instance.videos.exists()
        else:
            # For creates, only check provided data
            has_main_image = data.get("image")
            has_before = data.get("before_image")
            has_after = data.get("after_image")
            has_gallery_images = False  # Can't check yet, they're created separately
            has_videos = False  # Can't check yet, they're created separately

        # At least one image field must be provided OR we allow creation if user will add images/videos separately
        # Since gallery images and videos are created separately, we allow creation without main image
        # The frontend should validate that at least one media exists after creation.

        return data

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_thumbnail_url(self, obj):
        if obj.image:
            # Get the original image filename
            original_filename = os.path.basename(obj.image.name)
            thumbnail_filename = f"thumb_{original_filename}"

            # Construct thumbnail path
            thumbnail_path = f"/media/portfolio/thumbnails/{thumbnail_filename}"

            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(thumbnail_path)
            return thumbnail_path
        return None

    def get_gallery_image_url(self, obj):
        if obj.image:
            # Get the original image filename
            original_filename = os.path.basename(obj.image.name)
            gallery_filename = f"gallery_{original_filename}"

            # Construct the gallery image path
            gallery_path = f"/media/portfolio/gallery/{gallery_filename}"

            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(gallery_path)
            return gallery_path
        return None

    def get_before_image_url(self, obj):
        if obj.before_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.before_image.url)
            return obj.before_image.url
        return None

    def get_after_image_url(self, obj):
        if obj.after_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.after_image.url)
            return obj.after_image.url
        return None

    def get_before_thumbnail_url(self, obj):
        if obj.before_image:
            original_filename = os.path.basename(obj.before_image.name)
            thumbnail_filename = f"thumb_{original_filename}"
            thumbnail_path = f"/media/portfolio/before/thumbnails/{thumbnail_filename}"

            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(thumbnail_path)
            return thumbnail_path
        return None

    def get_after_thumbnail_url(self, obj):
        if obj.after_image:
            original_filename = os.path.basename(obj.after_image.name)
            thumbnail_filename = f"thumb_{original_filename}"
            thumbnail_path = f"/media/portfolio/after/thumbnails/{thumbnail_filename}"

            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(thumbnail_path)
            return thumbnail_path
        return None

    def get_image_count(self, obj):
        return obj.pictures.count()

    def get_has_before_after(self, obj):
        return bool(obj.before_image and obj.after_image)
