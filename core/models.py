from django.db import models
from django.core.exceptions import ValidationError


class SiteConfiguration(models.Model):
    """
    Singleton model for site-wide configuration.
    Only one instance should exist.
    """
    # Logo
    logo = models.ImageField(
        upload_to="site/",
        help_text="Main site logo (recommended: PNG with transparent background)",
        blank=True,
        null=True
    )
    
    # Hero Section
    hero_title = models.CharField(
        max_length=100,
        default="MPE i6",
        help_text="Main hero heading (e.g., 'MPE i6')"
    )
    hero_subtitle = models.CharField(
        max_length=150,
        default="Inline tray Sealer",
        help_text="Hero subheading (e.g., 'Inline tray Sealer')"
    )
    hero_description = models.TextField(
        default="High-speed inline tray sealer. Electric operation for maximum produce.",
        help_text="Hero description text"
    )
    hero_image = models.ImageField(
        upload_to="hero/",
        help_text="Large hero/showcase machine image",
        blank=True,
        null=True
    )
    hero_button_text = models.CharField(
        max_length=50,
        default="VIEW MACHINES",
        help_text="Text for the hero call-to-action button"
    )
    hero_button_link = models.CharField(
        max_length=200,
        default="#machines",
        help_text="Link for the hero button (e.g., '#machines' or '/shop/')"
    )
    
    # Feature Bullets
    feature_1 = models.CharField(max_length=100, default="UK manufacturing", blank=True)
    feature_2 = models.CharField(max_length=100, default="Service support", blank=True)
    feature_3 = models.CharField(max_length=100, default="Custom automation", blank=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=50, default="+44 1663 732700", blank=True)
    email = models.EmailField(default="sales@mpe-uk.com", blank=True)
    location = models.CharField(max_length=100, default="Derbyshire, UK", blank=True)
    
    # Social Media
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    facebook_url = models.URLField(blank=True, help_text="Facebook page URL")
    youtube_url = models.URLField(blank=True, help_text="YouTube channel URL")
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValidationError("Only one Site Configuration instance is allowed.")
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return "Site Configuration"
    
    @classmethod
    def get_config(cls):
        """Get or create the singleton configuration instance"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class BackgroundImage(models.Model):
    """Background images used for rotating hero/footer backgrounds."""
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="backgrounds/")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title or self.image.name


class MachineProduct(models.Model):
    """Marketing products shown on the Machines section of the website."""
    name = models.CharField(max_length=120)
    tagline = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="machines/", blank=True, null=True)
    spec_pdf = models.FileField(upload_to="spec_sheets/", blank=True, null=True)
    external_link = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class ShopProduct(models.Model):
    """Simple shop catalogue items (spares/consumables)."""

    CATEGORY_PARTS = "parts"
    CATEGORY_CONSUMABLES = "consumables"
    CATEGORY_ACCESSORIES = "accessories"
    CATEGORY_TOOLING = "tooling"

    CATEGORY_CHOICES = [
        (CATEGORY_PARTS, "Parts & Components"),
        (CATEGORY_CONSUMABLES, "Consumables"),
        (CATEGORY_ACCESSORIES, "Accessories"),
        (CATEGORY_TOOLING, "Tooling"),
    ]

    name = models.CharField(max_length=140)
    sku = models.CharField(max_length=60, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_PARTS)
    description = models.TextField(blank=True)
    price_gbp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to="shop/", blank=True, null=True)

    # Very lightweight stock flagging for now
    in_stock = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return f"{self.name}{' (' + self.sku + ')' if self.sku else ''}"
