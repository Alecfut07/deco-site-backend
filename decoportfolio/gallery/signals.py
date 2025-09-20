from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit
from imagekit.utils import get_cache
import os
from .models import PortfolioItem

@receiver(post_save, sender=PortfolioItem)
def generate_thumbnails(sender, instance, created, **kwargs):
    """Generate thumbnails when images are uploaded"""
    print(f"=== GENERATE THUMBNAILS SIGNAL FIRED for {instance.title} ===")
    print(f"Created: {created}")
    print(f"Has main image: {bool(instance.image)}")
    print(f"Has before image: {bool(instance.before_image)}")
    print(f"Has after image: {bool(instance.after_image)}")

    # Generate main image thumbnail
    if instance.image:
        try:
            # Create thumbnail using ImageKit processors
            from PIL import Image

            # Open image the original image
            img_path = instance.image.path
            img = Image.open(img_path)

            # Create thumbnail
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Save thumbnail
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)

            thumbnail_filename = f"thumb_{os.path.basename(instance.image.name)}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            print(f"Generated main thumbnail: {thumbnail_path}")
        except Exception as e:
            print(f"Error generating main thumbnail: {e}")

    # Generate before image thumbnail
    if instance.before_image:
        try:
            from PIL import Image
            
            img_path = instance.before_image.path
            img = Image.open(img_path)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'before', 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            thumbnail_filename = f"thumb_{os.path.basename(instance.before_image.name)}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            print(f"Generated before thumbnail: {thumbnail_path}")
        except Exception as e:
            print(f"Error generating before thumbnail: {e}")

    # Generate after image thumbnail
    if instance.after_image:
        try:
            from PIL import Image
            
            img_path = instance.after_image.path
            img = Image.open(img_path)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'after', 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)
            
            thumbnail_filename = f"thumb_{os.path.basename(instance.after_image.name)}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            print(f"Generated after thumbnail: {thumbnail_path}")
        except Exception as e:
            print(f"Error generating after thumbnail: {e}")

    print("=== GENERATE THUMBNAILS SIGNAL COMPLETED ===")
