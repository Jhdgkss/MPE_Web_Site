from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
import django.db.models.deletion

# -----------------------------------------------------------------------------
# 1. Site Configuration
# -----------------------------------------------------------------------------
class SiteConfiguration(models.Model):
    """
    Singleton model for site-wide configuration.
    """
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    
    # -- CONTACT --
    phone_number = models.CharField(max_length=50, default="+44 1663 732700", blank=True)
    email = models.EmailField(default="sales@mpe-uk.com", blank=True)
    location = models.CharField(max_length=100, default="Derbyshire, UK", blank=True)

    # -- SOCIAL --
    linkedin_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    # -- FEATURES --
    feature_1 = models.CharField(max_length=100, default="UK manufacturing", blank=True)
    feature_2 = models.CharField(max_length=100, default="Service support", blank=True)
    feature_3 = models.CharField(max_length=100, default="Custom automation", blank=True)

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def save(self, *args, **kwargs):
        if not self.pk and SiteConfiguration.objects.exists():
            raise ValidationError("Only one Site Configuration instance is allowed.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Site Configuration"

    @classmethod
    def get_config(cls):
        config, _ = cls.objects.get_or_create(pk=1)
        return config


# -----------------------------------------------------------------------------
# 2. Hero Slides
# -----------------------------------------------------------------------------
class HeroSlide(models.Model):
    STYLE_MACHINE = "machine"
    STYLE_NEWS = "news"
    
    STYLE_CHOICES = [
        (STYLE_MACHINE, "Machine Showcase"),
        (STYLE_NEWS, "News / Update"),
    ]

    # Content
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default=STYLE_MACHINE)
    title = models.CharField(max_length=120, help_text="Main heading or Machine Name")
    subtitle = models.CharField(max_length=180, blank=True, help_text="Tagline or short subtitle")
    description = models.TextField(blank=True, help_text="Paragraph text")

    # Media
    image = models.ImageField(upload_to="hero_slides/", blank=True, null=True, help_text="Main image")
    video = models.FileField(upload_to="hero_videos/", blank=True, null=True, help_text="Optional: Upload MP4 video (overrides image)")

    # Background Control
    card_background = models.ImageField(
        upload_to="hero_bgs/", 
        blank=True, 
        null=True, 
        help_text="Optional: Replace the dark box behind the machine with an image."
    )
    transparent_background = models.BooleanField(
        default=False, 
        help_text="Check this to remove the dark background box completely."
    )

    # Call to Action
    cta_text = models.CharField(max_length=50, blank=True, default="View Details")
    cta_link = models.CharField(max_length=240, blank=True, help_text="Internal path or full URL")

    # Settings
    show_features = models.BooleanField(default=True, help_text="Show the standard feature chips?")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self):
        return self.title


# -----------------------------------------------------------------------------
# 3. Other Models
# -----------------------------------------------------------------------------
class BackgroundImage(models.Model):
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="backgrounds/")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return self.title or self.image.name

class MachineProduct(models.Model):
    name = models.CharField(max_length=120)
    tagline = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="machines/", blank=True, null=True)
    spec_pdf = models.FileField(upload_to="spec_sheets/", blank=True, null=True)
    external_link = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["sort_order", "name"]
    def __str__(self): return self.name

class ShopProduct(models.Model):
    CATEGORY_CHOICES = [("parts", "Parts"), ("consumables", "Consumables"), ("accessories", "Accessories"), ("tooling", "Tooling")]
    name = models.CharField(max_length=140)
    sku = models.CharField(max_length=60, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="parts")
    description = models.TextField(blank=True)
    price_gbp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to="shop/", blank=True, null=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["sort_order", "name"]
    def __str__(self): return f"{self.name}"

class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    company_name = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["company_name", "user__username"]
    def __str__(self): return self.company_name

class StaffDocument(models.Model):
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, default="general")
    file = models.FileField(upload_to="staff_docs/")
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class CustomerMachine(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_machines")
    name = models.CharField(max_length=140)
    machine_type = models.CharField(max_length=30, default="tray_sealer")
    serial_number = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return f"{self.name}"

class CustomerDocument(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_documents")
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, default="general")
    file = models.FileField(upload_to="customer_docs/")
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class MachineMetric(models.Model):
    machine = models.ForeignKey("core.CustomerMachine", on_delete=models.CASCADE, related_name="metrics")
    metric_key = models.CharField(max_length=80)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField()
    class Meta: ordering = ["-timestamp"]

class MachineTelemetry(models.Model):
    machine_id = models.CharField(max_length=50)
    ppm = models.FloatField()
    temp = models.FloatField()
    batch_count = models.IntegerField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"{self.machine_id} - {self.created_at}"

# --- NEW MODEL: Distributor ---
class Distributor(models.Model):
    """
    Manages the Distribution Network cards on the homepage.
    """
    country_name = models.CharField(max_length=100, help_text="e.g. United Kingdom")
    flag_code = models.CharField(max_length=5, help_text="ISO 2-letter code (e.g. 'gb', 'us', 'ca')")
    description = models.TextField(help_text="Short text, e.g. 'Sales & Support partner'")
    
    cta_text = models.CharField(max_length=50, default="Contact Us", help_text="Button label")
    cta_link = models.CharField(max_length=200, help_text="URL or mailto: link")
    
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.country_name