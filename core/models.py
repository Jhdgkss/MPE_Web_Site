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


from django.contrib.auth import get_user_model

User = get_user_model()


class CustomerDocument(models.Model):
    """Documents visible to a specific customer in the Customer Portal."""

    CATEGORY_GENERAL = "general"
    CATEGORY_MANUALS = "manuals"
    CATEGORY_SPEC = "spec"
    CATEGORY_SERVICE = "service"
    CATEGORY_REPORTS = "reports"

    CATEGORY_CHOICES = [
        (CATEGORY_GENERAL, "General"),
        (CATEGORY_MANUALS, "Manuals"),
        (CATEGORY_SPEC, "Specification"),
        (CATEGORY_SERVICE, "Service"),
        (CATEGORY_REPORTS, "Reports"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_documents")
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_GENERAL)
    file = models.FileField(upload_to="customer_docs/")
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.customer})"


class CustomerMachine(models.Model):
    """A machine belonging to a customer (used by the portal dashboard)."""

    TYPE_TRAY_SEALER = "tray_sealer"
    TYPE_SANDWICH = "sandwich"
    TYPE_TOOLING = "tooling"
    TYPE_OTHER = "other"

    MACHINE_TYPE_CHOICES = [
        (TYPE_TRAY_SEALER, "Tray Sealer"),
        (TYPE_SANDWICH, "Sandwich Sealer"),
        (TYPE_TOOLING, "Tooling / Spares"),
        (TYPE_OTHER, "Other"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_machines")
    name = models.CharField(max_length=140)
    machine_type = models.CharField(max_length=30, choices=MACHINE_TYPE_CHOICES, default=TYPE_TRAY_SEALER)
    serial_number = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["customer", "name"]

    def __str__(self) -> str:
        return f"{self.name}{' (' + self.serial_number + ')' if self.serial_number else ''}"


class MachineMetric(models.Model):
    """Lightweight time-series metric data for a customer's machine.

    This is intentionally generic: you can store things like:
      - packs_per_minute
      - faults_today
      - temperature_1
      - temperature_2
    and then build dashboards on top.
    """

    machine = models.ForeignKey(CustomerMachine, on_delete=models.CASCADE, related_name="metrics")
    metric_key = models.CharField(max_length=80)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["machine", "metric_key", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.machine}: {self.metric_key}={self.value}{self.unit}"


class StaffDocument(models.Model):
    """Documents/forms visible to MPE staff in the Staff area."""

    CATEGORY_GENERAL = "general"
    CATEGORY_FORMS = "forms"
    CATEGORY_SERVICE = "service"
    CATEGORY_QA = "qa"
    CATEGORY_HR = "hr"

    CATEGORY_CHOICES = [
        (CATEGORY_GENERAL, "General"),
        (CATEGORY_FORMS, "Forms"),
        (CATEGORY_SERVICE, "Service"),
        (CATEGORY_QA, "QA / ISO"),
        (CATEGORY_HR, "HR"),
    ]

    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_GENERAL)
    file = models.FileField(upload_to="staff_docs/")
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return self.title
