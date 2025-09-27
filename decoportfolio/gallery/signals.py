import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import cache
from PIL import Image
from .models import PortfolioItem, Category, Service, BusinessInfo

def invalidate_related_caches(instance):
    """Smart cache invalidation for related data"""
    cache_keys_to_clear = []
    
    cache_keys_to_clear.extend([
        'portfolio_list_',
        f'portfolio_category_{instance.category.id if instance.category else "all"}_',
        f'portfolio_service_{instance.service.id if instance.service else "all"}_',
    ])

    # Clear search and filter caches
    cache_keys_to_clear.extend([
        'portfolio_search_',
        'portfolio_filter_',
        'portfolio_combined_',
    ])

    # Clear individual item cache
    cache_keys_to_clear.append(f'portfolio_item_{instance.id}')

    # Clear category and service related caches
    if hasattr(instance, 'category') and instance.category:
        cache_keys_to_clear.extend([
            f'category_{instance.category.id}',
            f'service_category_{instance.category.id}_',
        ])

    # Clear all matching cache keys
    for key in cache_keys_to_clear:
        cache.delete(key)
        print(f"Cleared cache key: {key}")

@receiver(post_save, sender=PortfolioItem)
def generate_thumbnails_and_invalidate_cache(sender, instance, created, **kwargs):
    """Generate thumbnails and invalidate related caches"""
    print(f"=== PROCESSING PORTFOLIO ITEM: {instance.title} ===")
    print(f"Created: {created}, Updated: not created")
    print(f"Has main image: {bool(instance.image)}")
    print(f"Has before image: {bool(instance.before_image)}")
    print(f"Has after image: {bool(instance.after_image)}")

    # Generate main image thumbnail and gallery image
    if instance.image:
        try:
            # Create thumbnail using ImageKit processors
            from PIL import Image

            # Open image the original image
            img_path = instance.image.path
            img = Image.open(img_path)

            # Create thumbnail (300x300)
            thumbnail_img = img.copy()
            thumbnail_img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Save thumbnail
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)

            thumbnail_filename = f"thumb_{os.path.basename(instance.image.name)}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            thumbnail_img.save(thumbnail_path, 'JPEG', quality=85)

            # Create gallery image (800x600)
            gallery_img = img.copy()
            gallery_img.thumbnail((800, 600), Image.Resampling.LANCZOS)

            # Save gallery image
            gallery_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'gallery')
            os.makedirs(gallery_dir, exist_ok=True)

            gallery_filename = f"gallery_{os.path.basename(instance.image.name)}"
            gallery_path = os.path.join(gallery_dir, gallery_filename)
            gallery_img.save(gallery_path, 'JPEG', quality=90)
            
            print(f"Generated main thumbnail: {thumbnail_path}")
            print(f"Generated main gallery image: {gallery_path}")
        except Exception as e:
            print(f"Error generating main images: {e}")

    # Generate before image thumbnail and gallery image
    if instance.before_image:
        try:
            from PIL import Image
            
            img_path = instance.before_image.path
            img = Image.open(img_path)

            # Create thumbnail (300x300)
            thumbnail_img = img.copy()
            thumbnail_img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Save thumbnail
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'before', 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            thumbnail_filename = f"thumb_{os.path.basename(instance.before_image.name)}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            thumbnail_img.save(thumbnail_path, 'JPEG', quality=85)

            # Create gallery image (800x600)
            gallery_img = img.copy()
            gallery_img.thumbnail((800, 600), Image.Resampling.LANCZOS)

            # Save gallery image
            gallery_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'before', 'gallery')
            os.makedirs(gallery_dir, exist_ok=True)

            gallery_filename = f"gallery_{os.path.basename(instance.before_image.name)}"
            gallery_path = os.path.join(gallery_dir, gallery_filename)
            gallery_img.save(gallery_path, 'JPEG', quality=90)
            
            print(f"Generated before thumbnail: {thumbnail_path}")
            print(f"Generated before gallery image: {gallery_path}")
        except Exception as e:
            print(f"Error generating before images: {e}")

    # Generate after image thumbnail and gallery image
    if instance.after_image:
        try:
            from PIL import Image
            
            img_path = instance.after_image.path
            img = Image.open(img_path)

            # Create thumbnail (300x300)
            thumbnail_img = img.copy()
            thumbnail_img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'after', 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            thumbnail_filename = f"thumb_{os.path.basename(instance.after_image.name)}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            thumbnail_img.save(thumbnail_path, 'JPEG', quality=85)

            # Create gallery image (800x600)
            gallery_img = img.copy()
            gallery_img.thumbnail((800, 600), Image.Resampling.LANCZOS)

            # Save gallery image
            gallery_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'after', 'gallery')
            os.makedirs(gallery_dir, exist_ok=True)

            gallery_filename = f"gallery_{os.path.basename(instance.after_image.name)}"
            gallery_path = os.path.join(gallery_dir, gallery_filename)
            gallery_img.save(gallery_path, 'JPEG', quality=90)
            
            print(f"Generated after thumbnail: {thumbnail_path}")
            print(f"Generated after gallery image: {gallery_path}")
        except Exception as e:
            print(f"Error generating after images: {e}")

    # Smart cache invalidation
    invalidate_related_caches(instance)

    print("=== CACHE INVALIDATION COMPLETED ===\n")

@receiver(post_delete, sender=PortfolioItem)
def cleanup_and_invalidate_cache(sender, instance, **kwargs):
    """Cleanup files and invalidate cache when item is deleted"""
    print(f"=== DELETING PORTFOLIO ITEM: {instance.title} ===")

    # Clean up images files (optional)
    # ... (add file cleanup logic if needed)

    # Invalidate related caches
    invalidate_related_caches(instance)

    print("=== DELETION AND CACHE INVALIDATION COMPLETED ===\n")

@receiver(post_save, sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    """Invalidate cache when category is updated"""
    cache_keys = [
        f'category_{instance.id}',
        'portfolio_list_',
        'portfolio_search_',
        'portfolio_filter_',
        'portfolio_combined_',
    ]

    for key in cache_keys:
        cache.delete(key)
    print(f"Cleared category-related caches for: {instance.name}")

@receiver(post_save, sender=Service)
def invalidate_service_cache(sender, instance, **kwargs):
    """Invalidate cache when service is updated"""
    cache_keys = [
        f'service_{instance.id}',
        f'service_category_{instance.category.id}_',
        'portfolio_list_',
        'portfolio_search_',
        'portfolio_filter_',
        'portfolio_combined_',
    ]

    for key in cache_keys:
        cache.delete(key)
    print(f"Cleared service-related caches for: {instance.name}")
