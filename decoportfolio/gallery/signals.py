import os
import cv2
import numpy as np
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth.models import Group, Permission
from PIL import Image
from .models import PortfolioItem, Category, Service, BusinessInfo, PortfolioImage, PortfolioVideo

def ensure_family_group_exists():
    group, created = Group.objects.get_or_create(name='Family')
    # Optionally assign specific permissions
    # e.g. group.permissions.add(Permission.objects.get(codename='change_portfolioitem'))

def invalidate_related_caches(instance):
    """Smart cache invalidation for related data"""
    cache_keys_to_clear = []

    # Handle PortfolioImage and PortfolioVideo instances
    if isinstance(instance, (PortfolioImage, PortfolioVideo)):
        # Get the parent PortfolioItem
        portfolio_item = instance.portfolio_item
        instance = portfolio_item  # Use portfolio_item for cache invalidation
    
    # Check if instance has required attributes (must be PortfolioItem)
    if not hasattr(instance, 'category'):
        return
    
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
    if instance.category:
        cache_keys_to_clear.extend([
            f'category_{instance.category.id}',
            f'service_category_{instance.category.id}_',
        ])

    # Clear all matching cache keys
    for key in cache_keys_to_clear:
        cache.delete(key)
        print(f"Cleared cache key: {key}")

@receiver(post_save, sender=PortfolioImage)
def generate_portfolio_image_thumbnails(sender, instance, created, **kwargs):
    """Generate thumbnails for portfolio images"""
    if created and instance.image:
        print(f"=== PROCESSING PORTFOLIO IMAGE: {instance.id} ===")
        print(f"Portfolio Item: {instance.portfolio_item.title}")
        print(f"Image: {instance.image.name}")

        def generate_image_variants(image_field, base_dir, image_type):
            """Helper function to generate thumbnail and gallery images"""
            if not image_field:
                return
            
            try:
                # Check if image file exists on disk
                if not os.path.exists(image_field.path):
                    print(f"Image file not found on disk: {image_field.path}")
                    return
                
                # Open the original image
                img = Image.open(image_field.path)

                # Get original format and determine output format
                original_format = img.format
                output_format = 'JPEG' if original_format in ['JPEG', 'JPG'] else 'PNG'

                # Create thumbnail (300x300)
                thumbnail_img = img.copy()
                thumbnail_img.thumbnail((300, 300), Image.Resampling.LANCZOS)

                # Save thumbnail
                thumbnail_dir = os.path.join(settings.MEDIA_ROOT, base_dir, 'thumbnails')
                os.makedirs(thumbnail_dir, exist_ok=True)

                thumbnail_filename = f"thumb_{os.path.basename(image_field.name)}"
                thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

                # Convert to RGB if saving as JPEG (JPEG doesn't support transparency)
                if output_format == 'JPEG' and thumbnail_img.mode in ['RGBA', 'LA', 'P']:
                    thumbnail_img = thumbnail_img.convert('RGB')
                
                thumbnail_img.save(thumbnail_path, output_format, quality=85)

                # Create gallery image (800x600 max)
                gallery_img = img.copy()
                gallery_img.thumbnail((800, 600), Image.Resampling.LANCZOS)

                gallery_dir = os.path.join(settings.MEDIA_ROOT, base_dir, 'gallery')
                os.makedirs(gallery_dir, exist_ok=True)

                gallery_filename = f"gallery_{os.path.basename(image_field.name)}"
                gallery_path = os.path.join(gallery_dir, gallery_filename)

                # Convert to RGB if saving as JPEG
                if output_format == 'JPEG' and gallery_img.mode in ['RGBA', 'LA', 'P']:
                    gallery_img = gallery_img.convert('RGB')

                gallery_img.save(gallery_path, output_format, quality=90)
                
                print(f"Generated {image_type} thumbnail: {thumbnail_path}")
                print(f"Generated {image_type} gallery image: {gallery_path}")
            
            except Exception as e:
                print(f"Error generating {image_type} images: {e}")
            
        # Generate image variants
        generate_image_variants(instance.image, 'portfolio/images', 'portfolio_image')

        # Invalidate parent PortfolioItem cache
        invalidate_related_caches(instance)

@receiver(post_save, sender=PortfolioVideo)
def generate_video_thumbnail(sender, instance, created, **kwargs):
    """Generate thumbnail from video"""
    if created and instance.video:
        print(f"=== PROCESSING PORTFOLIO VIDEO: {instance.id} ===")
        print(f"Portfolio Item: {instance.portfolio_item.title}")
        print(f"Video: {instance.video.name}")

        try:
            # Check if video file exists on disk
            if not os.path.exists(instance.video.path):
                print(f"Video file not found on disk: {instance.video.path}")
                return
            
            # Open video file with OpenCV
            cap = cv2.VideoCapture(instance.video.path)

            if not cap.isOpened():
                print(f"Error opening video file: {instance.video.path}")
                return
            
            # Get total number of frames
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Calculate frame position (use 1 second or 10% of video, whichever is smaller)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30  # Default to 30 fps if not available
            frame_position = min(int(fps), total_frames // 10) if total_frames > 0 else 0

            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)

            # Read frame
            ret, frame = cap.read()

            if not ret or frame is None:
                # If frame extraction failed, try middle of video
                cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2 if total_frames > 0 else 0) 
                ret, frame = cap.read()

            cap.release()

            if not ret or frame is None:
                print(f"Error raeding frame from video: {instance.video.path}")
                return
            
            # Convert BGR to RGB (OpenCV uses BGR, PIL uses RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)

            # Resize to thumbnail size (300x300)
            pil_image.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Create thumbnail directory
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'portfolio/videos/thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)

            # Generate thumbnail filename
            video_basename = os.path.basename(instance.video.name)
            video_name_without_ext = os.path.splitext(video_basename)[0]
            thumbnail_filename = f"{video_name_without_ext}.jpg"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

            # Convert to RGB if needed (for JPEG compatibility)
            if pil_image.mode in ['RGBA', 'LA', 'P']:
                pil_image = pil_image.convert('RGB')

            # Save thumbnail
            pil_image.save(thumbnail_path, 'JPEG', quality=85)

            # Update the thumbnail field in the model
            # We need to save the relative path from MEDIA_ROOT
            thumbnail_relative_path = f"portfolio/videos/thumbnails/{thumbnail_filename}"
            instance.thumbnail.name = thumbnail_relative_path
            instance.save(update_fields=['thumbnail'])

            print(f"Generated video thumbnail: {thumbnail_path}")
            print(f"=== PORTFOLIO VIDEO PROCESSING COMPLETED ===\n")

        except Exception as e:
            print(f"Error generating video thumbnail: {e}")
            import traceback
            traceback.print_exc()
        
        # Invalidate parent PortfolioItem cache
        invalidate_related_caches(instance)

@receiver(post_save, sender=PortfolioItem)
def generate_thumbnails_and_invalidate_cache(sender, instance, created, **kwargs):
    """Generate thumbnails and invalidate related caches"""
    print(f"=== PROCESSING PORTFOLIO ITEM: {instance.title} ===")
    print(f"Created: {created}, Updated: {not created}")
    print(f"Has main image: {bool(instance.image)}")
    print(f"Has before image: {bool(instance.before_image)}")
    print(f"Has after image: {bool(instance.after_image)}")

    def generate_image_variants(image_field, base_dir, image_type):
        """Helper function to generate thumbnail and gallery images"""
        if not image_field:
            return
        
        try:
            # Check if image file exists on disk
            if not os.path.exists(image_field.path):
                print(f"Image file not found on disk: {image_field.path}")
                return
            
            # Open the original image
            img = Image.open(image_field.path)

            # Get original format and determine output format
            original_format = img.format
            output_format = 'JPEG' if original_format in ['JPEG', 'JPG'] else 'PNG'

            # Create thumbnail (300x300)
            thumbnail_img = img.copy()
            thumbnail_img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Save thumbnail
            thumbnail_dir = os.path.join(settings.MEDIA_ROOT, base_dir, 'thumbnails')
            os.makedirs(thumbnail_dir, exist_ok=True)

            thumbnail_filename = f"thumb_{os.path.basename(image_field.name)}"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

            # Convert to RGB if saving as JPEG (JPEG doesn't support transparency)
            if output_format == 'JPEG' and thumbnail_img.mode in ['RGBA', 'LA', 'P']:
                thumbnail_img = thumbnail_img.convert('RGB')

            thumbnail_img.save(thumbnail_path, output_format, quality=85)

            # Create gallery image (800x600 max)
            gallery_img = img.copy()
            gallery_img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            
            gallery_dir = os.path.join(settings.MEDIA_ROOT, base_dir, 'gallery')
            os.makedirs(gallery_dir, exist_ok=True)

            gallery_filename = f"gallery_{os.path.basename(image_field.name)}"
            gallery_path = os.path.join(gallery_dir, gallery_filename)

            # Convert to RGB if saving as JPEG
            if output_format == 'JPEG' and gallery_img.mode in ['RGBA', 'LA', 'P']:
                gallery_img = gallery_img.convert('RGB')

            gallery_img.save(gallery_path, output_format, quality=90)

            print(f"Generated {image_type} thumbnail: {thumbnail_path}")
            print(f"Generated {image_type} gallery image: {gallery_path}")
        
        except Exception as e:
            print(f"Error generating {image_type} images: {e}")

    # Generate main image variants
    if instance.image:
        generate_image_variants(instance.image, 'portfolio', 'main')
    
    # Generate before image variants
    if instance.before_image:
        generate_image_variants(instance.before_image, 'portfolio/before', 'before')
    
    # Generate after image variants
    if instance.after_image:
        generate_image_variants(instance.after_image, 'portfolio/after', 'after')

    # Smart cache invalidation
    invalidate_related_caches(instance)

    print("=== CACHE INVALIDATION COMPLETED ===\n")

@receiver(post_delete, sender=PortfolioItem)
def cleanup_and_invalidate_cache(sender, instance, **kwargs):
    """Cleanup files and invalidate cache when item is deleted"""
    print(f"=== DELETING PORTFOLIO ITEM: {instance.title} ===")

    # Clean up image files
    files_to_delete = []

    # Main image and its generated files
    if instance.image:
        try:
            # Original main image
            if os.path.exists(instance.image.path):
                files_to_delete.append(instance.image.path)
            
            # Main image thumbnail
            thumbnail_filename = f"thumb_{os.path.basename(instance.image.name)}"
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'thumbnails', thumbnail_filename)
            if os.path.exists(thumbnail_path):
                files_to_delete.append(thumbnail_path)

            # Main image gallery version
            gallery_filename = f"gallery_{os.path.basename(instance.image.name)}"
            gallery_path = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'gallery', gallery_filename)
            if os.path.exists(gallery_path):
                files_to_delete.append(gallery_path)

        except Exception as e:
            print(f"Error preparing main image cleanup: {e}")
    
    # Before image and its generated files
    if instance.before_image:
        try:
            # Original before image
            if os.path.exists(instance.before_image.path):
                files_to_delete.append(instance.before_image.path)
            
            # Before image thumbnail
            thumbnail_filename = f"thumb_{os.path.basename(instance.before_image.name)}"
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'before', 'thumbnails', thumbnail_filename)
            if os.path.exists(thumbnail_path):
                files_to_delete.append(thumbnail_path)

            # Before image gallery version
            gallery_filename = f"gallery_{os.path.basename(instance.before_image.name)}"
            gallery_path = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'before', 'gallery', gallery_filename)
            if os.path.exists(gallery_path):
                files_to_delete.append(gallery_path)

        except Exception as e:
            print(f"Error preparing before image cleanup: {e}")
        
    # After image and its generated files
    if instance.after_image:
        try:
            # Original after image
            if os.path.exists(instance.after_image.path):
                files_to_delete.append(instance.after_image.path)
            
            # After image thumbnail
            thumbnail_filename = f"thumb_{os.path.basename(instance.after_image.name)}"
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'after', 'thumbnails', thumbnail_filename)
            if os.path.exists(thumbnail_path):
                files_to_delete.append(thumbnail_path)
            
            # After image gallery version
            gallery_filename = f"gallery_{os.path.basename(instance.after_image.name)}"
            gallery_path = os.path.join(settings.MEDIA_ROOT, 'portfolio', 'after', 'gallery', gallery_filename)
            if os.path.exists(gallery_path):
                files_to_delete.append(gallery_path)
            
        except Exception as e:
            print(f"Error preparing after image cleanup: {e}")
    
    # Delete all related PortfolioImage files
    try:
        for portfolio_image in instance.pictures.all():
            # Delete original image
            if portfolio_image.image and os.path.exists(portfolio_image.image.path):
                files_to_delete.append(portfolio_image.image.path)

            # Delete thumbnail
            thumbnail_filename = f"thumb_{os.path.basename(portfolio_image.image.name)}"
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'portfolio/images/thumbnails', thumbnail_filename)
            if os.path.exists(thumbnail_path):
                files_to_delete.append(thumbnail_path)
            
            # Delete gallery image
            gallery_filename = f"gallery_{os.path.basename(portfolio_image.image.name)}"
            gallery_path = os.path.join(settings.MEDIA_ROOT, 'portfolio/images/gallery', gallery_filename)
            if os.path.exists(gallery_path):
                files_to_delete.append(gallery_path)
    except Exception as e:
        print(f"Error preparing PortfolioImage cleanup: {e}")
    
    # Delete all related PortfolioVideo Files
    try:
        for portfolio_video in instance.videos.all():
            # Delete original video
            if portfolio_video.video and os.path.exists(portfolio_video.video.path):
                files_to_delete.append(portfolio_video.video.path)

            # Delete thumbnail
            if portfolio_video.thumbnail and os.path.exists(portfolio_video.thumbnail.path):
                files_to_delete.append(portfolio_video.thumbnail.path)
    except Exception as e:
        print(f"Error preparing PortfolioVideo cleanup: {e}")
    
    # Actually delete the files
    deleted_count = 0
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_count += 1
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    print(f"Cleaned up {deleted_count} files")

    # Invalidate related caches
    invalidate_related_caches(instance)

    print("=== DELETION AND CACHE INVALIDATION COMPLETED ===\n")

@receiver(post_delete, sender=PortfolioImage)
def cleanup_portfolio_image(sender, instance, **kwargs):
    """Cleanup files and invalidate cache when PortfolioImage is deleted"""
    print(f"=== DELETING PORTFOLIO IMAGE: {instance.id} ===")

    files_to_delete = []

    # Delete original image
    if instance.image and os.path.exists(instance.image.path):
        files_to_delete.append(instance.image.path)

    # Delete thumbnail
    try:
        thumbnail_filename = f"thumb_{os.path.basename(instance.image.name)}"
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'portfolio/images/thumbnails', thumbnail_filename)
        if os.path.exists(thumbnail_path):
            files_to_delete.append(thumbnail_path)
    except Exception as e:
        print(f"Error preparing thumbnail cleanup: {e}")
    
    # Delete gallery image
    try:
        gallery_filename = f"gallery_{os.path.basename(instance.image.name)}"
        gallery_path = os.path.join(settings.MEDIA_ROOT, 'portfolio/images/gallery', gallery_filename)
        if os.path.exists(gallery_path):
            files_to_delete.append(gallery_path)
    except Exception as e:
        print(f"Error preparing gallery image cleanup: {e}")

    # Actually delete the files
    deleted_count = 0
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_count += 1
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    
    print(f"Cleaned up {deleted_count} files")

    # Invalidate parent PortfolioItem cache
    invalidate_related_caches(instance)

    print("=== PORTFOLIO IMAGE DELETION COMPLETED ===\n")

@receiver(post_delete, sender=PortfolioVideo)
def cleanup_portfolio_video(sender, instance, **kwargs):
    """Cleanup files and invalidate cache when PortfolioVideo is deleted"""
    print(f"=== DELETING PORTFOLIO VIDEO: {instance.id} ===")

    files_to_delete = []

    # Delete original video
    if instance.video and os.path.exists(instance.video.path):
        files_to_delete.append(instance.video.path)
    
    # Delete thumbnail
    if instance.thumbnail and os.path.exists(instance.thumbnail.path):
        files_to_delete.append(instance.thumbnail.path)

    # Actually delete the files
    deleted_count = 0
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_count += 1
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    print(f"Cleaned up {deleted_count} files")

    # Invalidate parent PortfolioItem cache
    invalidate_related_caches(instance)

    print("=== PORTFOLIO VIDEO DELETION COMPLETED ===\n")

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

@receiver(post_save, sender=BusinessInfo)
def invalidate_business_cache(sender, instance, **kwargs):
    """Invalidate cache when business info is updated"""
    cache_keys = [
        'business_info_',
        'business_info_list_',
    ]

    for key in cache_keys:
        cache.delete(key)
    print(f"Cleared business info caches")