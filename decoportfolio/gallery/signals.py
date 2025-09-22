from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import cache
import os
from .models import PortfolioItem

@receiver(post_save, sender=PortfolioItem)
def invalidate_portfolio_cache(sender, instance, **kwargs):
    """Clear related caches when portfolio item is saved"""
    print("Invalidating portfolio caches...")

    # Clear list caches (all variations)
    cache.delete_many([
        'portfolio_list_',
        f'portfolio_list_category_{instance.category.name.lower()}',
        'portfolio_search_',
        'portfolio_filter_',
    ])

    # Clear individual item cache
    cache.delete(f'portfolio_item_{instance.id}')

    print("Portfolio caches invalidated")

@receiver(post_delete, sender=PortfolioItem)
def invalidate_portfolio_cache_on_delete(sender, instance, **kwargs):
    """Clear related caches when portfolio item is deleted"""
    print("Invalidating portfolio caches (delete)...")

    # Clear list caches
    cache.delete_many([
        'portfolio_list_',
        f'portfolio_list_category_{instance.category.name.lower()}',
        'portfolio_search_',
        'portfolio_filter_',
    ])

    # Clear individual item cache
    cache.delete(f'portfolio_item_{instance.id}')

    print("Portfolio caches invalidated")


@receiver(post_save, sender=PortfolioItem)
def generate_thumbnails(sender, instance, created, **kwargs):
    """Generate thumbnails when images are uploaded"""
    print(f"=== GENERATE THUMBNAILS SIGNAL FIRED for {instance.title} ===")
    print(f"Created: {created}")
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

    print("=== GENERATE THUMBNAILS SIGNAL COMPLETED ===")
