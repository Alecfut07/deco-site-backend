from django.db import models
from django.utils import timezone
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

    def __str__(self):
        return self.name
    
class PortfolioItem(models.Model):
    title = models.CharField(max_length=200)
    # image = models.ImageField(upload_to='porfolio/')
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='portfolio_items')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio_items')

    # Multiple images (at least one required)
    images = models.JSONField(default=list, help_text="List of image URLs")

    # Before/After images (optional)
    before_image = models.ImageField(upload_to='portfolio/before/', blank=True, null=True)
    after_image = models.ImageField(upload_to='portfolio/after/', blank=True, null=True)

    is_before_after = models.BooleanField(default=False, help_text="Is this a before/after project?")
    
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return self.title

    def get_primary_image(self):
        """Get the first image from the images list"""
        if self.images:
            return self.images[0]
        return None
    
    def has_before_after(self):
        """Check if this portfolio item has before/after images"""
        return bool(self.before_image and self.after_image)
