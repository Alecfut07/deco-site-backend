from django.db import models
from django.utils import timezone
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit, ResizeToCover
from category.models import Category

class BusinessInfo(models.Model):
    company_name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    years_experience = models.IntegerField(default=0)
    specialties = models.TextField(help_text="Comma-separated list of specialties")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Business Information'
        verbose_name_plural = 'Business Information'

    def __str__(self):
        return self.company_name

class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_range = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    is_active = models.BooleanField(default=True, help_text="Hide inactive services")
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = 'Services'
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['display_order']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name
    
class PortfolioItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='portfolio_items')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio_items')

    # Main image (for admin upload and primary display)
    image = models.ImageField(upload_to='portfolio/main/', help_text="Main project image")

    # Thumbnails (auto-generated from main image)
    thumbnail = ProcessedImageField(
        upload_to='portfolio/thumbnails/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True
    )

    # Gallery image (optimized for gallery display)
    gallery_image = ProcessedImageField(
        upload_to='portfolio/gallery/',
        processors=[ResizeToFit(800, 600)],
        format=f'WebP',
        options={'quality': 90},
        blank=True,
        null=True
    )

    # Before/After images (optional)
    before_image = models.ImageField(upload_to='portfolio/before/', blank=True, null=True)
    after_image = models.ImageField(upload_to='portfolio/after/', blank=True, null=True)

    # Before/After thumbnails (auto-generated)
    before_thumbnail = ProcessedImageField(
        upload_to='portfolio/before/thumbnails/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True
    )

    after_thumbnail = ProcessedImageField(
        upload_to='portfolio/after/thumbnails/',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True
    )

    # Before/After flag
    is_before_after = models.BooleanField(default=False, help_text="Is this a before/after project?")
    
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['category', 'upload_date']),
            models.Index(fields=['service', 'upload_date']),
            models.Index(fields=['is_before_after', 'upload_date']),
            models.Index(fields=['title']), # For search optimization
        ]

    def __str__(self):
        return self.title

    def get_primary_image(self):
        """Get the main image"""
        if self.image:
            return self.image.url
        return None
    
    def has_before_after(self):
        """Check if this portfolio item has before/after images"""
        return bool(self.before_image and self.after_image)

class PortfolioImage(models.Model):
    portfolio_item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name='pictures'
    )
    image = models.ImageField(upload_to='portfolio/images/')

    # Thumbnails (auto-generated)
    thumbnail = ProcessedImageField(
        upload_to='portfolio/images/thumbnails/',
        processors = [ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 85},
        blank=True,
        null=True
    )

    # Gallery image (optimized for gallery display)
    gallery_image = ProcessedImageField(
        upload_to='portfolio/images/gallery/',
        processors=[ResizeToFit(800, 600)],
        format='WebP',
        options={'quality': 90},
        blank=True,
        null=True
    )

    caption = models.CharField(max_length=200, blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return f"{self.portfolio_item.title} - Image {self.id}"

class PortfolioVideo(models.Model):
    portfolio_item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    video = models.FileField(upload_to='portfolio/videos/')

    # Thumbnail (auto-generated from video)
    thumbnail = models.ImageField(
        upload_to='portfolio/videos/thumbnails/',
        blank=True,
        null=True,
        help_text="Auto-generated from video"
    )

    caption = models.CharField(max_length=200, blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'created_at']
    
    def __str__(self):
        return f"{self.portfolio_item.title} - Video {self.id}"
