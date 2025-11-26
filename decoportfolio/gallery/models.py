from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, ResizeToFit, ResizeToCover
from category.models import Category


class FamilyMemberManager(BaseUserManager):
    """Manager for FamilyMember model"""

    def create_user(self, username, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not username:
            raise ValueError("The Username field must be set")
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class FamilyMember(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for frontend family members
    Completely separate from Django Admin users.
    """

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        default=False, help_text="Can access admin dashboard from frontend"
    )
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = FamilyMemberManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Family Member"
        verbose_name_plural = "Family Members"
        # Add permissions for all models
        permissions = [
            # Portfolio Item Permissions
            ("view_portfolioitem", "Can view portfolio items"),
            ("add_portfolioitem", "Can add portfolio items"),
            ("change_portfolioitem", "Can change portfolio items"),
            ("delete_portfolioitem", "Can delete portfolio items"),
            # Porfolio Image Permissions
            ("view_portfolioimage", "Can view portfolio images"),
            ("add_portfolioimage", "Can add portfolio images"),
            ("change_portfolioimage", "Can change portfolio images"),
            ("delete_portfolioimage", "Can delete portfolio images"),
            # Portfolio Video Permissions
            ("view_portfoliovideo", "Can view portfolio videos"),
            ("add_portfoliovideo", "Can add portfolio videos"),
            ("change_portfoliovideo", "Can change portfolio videos"),
            ("delete_portfoliovideo", "Can delete portfolio videos"),
            # Category Permissions
            ("view_category", "Can view categories"),
            ("add_category", "Can add categories"),
            ("change_category", "Can change categories"),
            ("delete_category", "Can delete categories"),
            # Service Permissions
            ("view_service", "Can view services"),
            ("add_service", "Can add services"),
            ("change_service", "Can change services"),
            ("delete_service", "Can delete services"),
            # Business Info Permissions
            ("view_businessinfo", "Can view business info"),
            ("add_businessinfo", "Can add business info"),
            ("change_businessinfo", "Can change business info"),
            ("delete_businessinfo", "Can delete business info"),
        ]

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Return the full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self):
        """Return the short name"""
        return self.first_name or self.username


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
        verbose_name = "Business Information"
        verbose_name_plural = "Business Information"

    def __str__(self):
        return self.company_name


class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_range = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="services"
    )
    is_active = models.BooleanField(default=True, help_text="Hide inactive services")
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "Services"
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["display_order"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class PortfolioItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="portfolio_items"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="portfolio_items",
    )

    # Main image (for admin upload and primary display)
    image = models.ImageField(
        upload_to="portfolio/main/", help_text="Main project image"
    )

    # Thumbnails (auto-generated from main image)
    thumbnail = ProcessedImageField(
        upload_to="portfolio/thumbnails/",
        processors=[ResizeToFill(300, 300)],
        format="JPEG",
        options={"quality": 85},
        blank=True,
        null=True,
    )

    # Gallery image (optimized for gallery display)
    gallery_image = ProcessedImageField(
        upload_to="portfolio/gallery/",
        processors=[ResizeToFit(800, 600)],
        format=f"WebP",
        options={"quality": 90},
        blank=True,
        null=True,
    )

    # Before/After images (optional)
    before_image = models.ImageField(
        upload_to="portfolio/before/", blank=True, null=True
    )
    after_image = models.ImageField(upload_to="portfolio/after/", blank=True, null=True)

    # Before/After thumbnails (auto-generated)
    before_thumbnail = ProcessedImageField(
        upload_to="portfolio/before/thumbnails/",
        processors=[ResizeToFill(300, 300)],
        format="JPEG",
        options={"quality": 85},
        blank=True,
        null=True,
    )

    after_thumbnail = ProcessedImageField(
        upload_to="portfolio/after/thumbnails/",
        processors=[ResizeToFill(300, 300)],
        format="JPEG",
        options={"quality": 85},
        blank=True,
        null=True,
    )

    # Before/After flag
    is_before_after = models.BooleanField(
        default=False, help_text="Is this a before/after project?"
    )

    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-upload_date"]
        indexes = [
            models.Index(fields=["category", "upload_date"]),
            models.Index(fields=["service", "upload_date"]),
            models.Index(fields=["is_before_after", "upload_date"]),
            models.Index(fields=["title"]),  # For search optimization
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
        PortfolioItem, on_delete=models.CASCADE, related_name="pictures"
    )
    image = models.ImageField(upload_to="portfolio/images/")

    # Thumbnails (auto-generated)
    thumbnail = ProcessedImageField(
        upload_to="portfolio/images/thumbnails/",
        processors=[ResizeToFill(300, 300)],
        format="JPEG",
        options={"quality": 85},
        blank=True,
        null=True,
    )

    # Gallery image (optimized for gallery display)
    gallery_image = ProcessedImageField(
        upload_to="portfolio/images/gallery/",
        processors=[ResizeToFit(800, 600)],
        format="WebP",
        options={"quality": 90},
        blank=True,
        null=True,
    )

    caption = models.CharField(max_length=200, blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return f"{self.portfolio_item.title} - Image {self.id}"


class PortfolioVideo(models.Model):
    portfolio_item = models.ForeignKey(
        PortfolioItem, on_delete=models.CASCADE, related_name="videos"
    )
    video = models.FileField(upload_to="portfolio/videos/")

    # Thumbnail (auto-generated from video)
    thumbnail = models.ImageField(
        upload_to="portfolio/videos/thumbnails/",
        blank=True,
        null=True,
        help_text="Auto-generated from video",
    )

    caption = models.CharField(max_length=200, blank=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return f"{self.portfolio_item.title} - Video {self.id}"
