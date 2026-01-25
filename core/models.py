from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
import django.db.models.deletion


class SiteConfiguration(models.Model):
    """Singleton model for site-wide configuration."""

    logo = models.ImageField(
        upload_to="site/",
        help_text="Main site logo (recommended: PNG with transparent background)",
        blank=True,
        null=True,
    )

    hero_title = models.CharField(max_length=100, default="MPE i6", help_text="Main hero heading")
    hero_subtitle = models.CharField(max_length=150, default="Inline tray Sealer", help_text="Hero subheading")
    hero_description = models.TextField(
        default="High-speed inline tray sealer. Electric operation for maximum produce.",
        help_text="Hero description text",
    )
    hero_image = models.ImageField(upload_to="hero/", help_text="Large hero/showcase machine image", blank=True, null=True)
    hero_button_text = models.CharField(max_length=50, default="VIEW MACHINES", help_text="Hero button text")
    hero_button_link = models.CharField(max_length=200, default="#machines", help_text="Hero button link")

    feature_1 = models.CharField(max_length=100, default="UK manufacturing", blank=True)
    feature_2 = models.CharField(max_length=100, default="Service support", blank=True)
    feature_3 = models.CharField(max_length=100, default="Custom automation", blank=True)

    phone_number = models.CharField(max_length=50, default="+44 1663 732700", blank=True)
    email = models.EmailField(default="sales@mpe-uk.com", blank=True)
    location = models.CharField(max_length=100, default="Derbyshire, UK", blank=True)

    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    facebook_url = models.URLField(blank=True, help_text="Facebook page URL")
    youtube_url = models.URLField(blank=True, help_text="YouTube channel URL")

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


class BackgroundImage(models.Model):
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="backgrounds/")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title or self.image.name


class HeroSlide(models.Model):
    KIND_IMAGE = "image"
    KIND_EMBED = "embed"
    KIND_CHOICES = [
        (KIND_IMAGE, "Image"),
        (KIND_EMBED, "Embedded video (URL)"),
    ]

    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=180, blank=True)
    body = models.TextField(blank=True)

    cta_text = models.CharField(max_length=50, blank=True)
    cta_link = models.CharField(max_length=240, blank=True, help_text="Internal path or full URL")

    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=KIND_IMAGE)
    image = models.ImageField(upload_to="hero_slides/", blank=True, null=True)
    embed_url = models.URLField(blank=True, help_text="YouTube/Vimeo embed URL")

    bullet_1 = models.CharField(max_length=120, blank=True)
    bullet_2 = models.CharField(max_length=120, blank=True)
    bullet_3 = models.CharField(max_length=120, blank=True)

    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "created_at"]

    def __str__(self) -> str:
        return self.title


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

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class ShopProduct(models.Model):
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

    in_stock = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return f"{self.name}{' (' + self.sku + ')' if self.sku else ''}"


# -----------------------------------------------------------------------------
# Customer & Staff portal models (created by migration 0005_customer_portal_models)
# -----------------------------------------------------------------------------

class CustomerProfile(models.Model):
    """Marks a non-staff User as a 'Customer portal' user and stores basic account info."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    company_name = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=True, help_text="Disable to block portal access without deleting the user.")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["company_name", "user__username"]

    def __str__(self) -> str:
        return self.company_name or self.user.get_username()


class StaffDocument(models.Model):
    CATEGORY_CHOICES = [
        ("general", "General"),
        ("forms", "Forms"),
        ("service", "Service"),
        ("qa", "QA / ISO"),
        ("hr", "HR"),
    ]
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="general")
    file = models.FileField(upload_to="staff_docs/")
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return self.title


class CustomerMachine(models.Model):
    TYPE_CHOICES = [
        ("tray_sealer", "Tray Sealer"),
        ("sandwich", "Sandwich Sealer"),
        ("tooling", "Tooling / Spares"),
        ("other", "Other"),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_machines")
    name = models.CharField(max_length=140)
    machine_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="tray_sealer")
    serial_number = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["customer", "name"]

    def __str__(self) -> str:
        return f"{self.customer.get_username()} — {self.name}"


class CustomerDocument(models.Model):
    CATEGORY_CHOICES = [
        ("general", "General"),
        ("manuals", "Manuals"),
        ("spec", "Specification"),
        ("service", "Service"),
        ("reports", "Reports"),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_documents")
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="general")
    file = models.FileField(upload_to="customer_docs/")
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.customer.get_username()} — {self.title}"


class MachineMetric(models.Model):
    machine = models.ForeignKey("core.CustomerMachine", on_delete=django.db.models.deletion.CASCADE, related_name="metrics")
    metric_key = models.CharField(max_length=80)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["machine", "metric_key", "timestamp"], name="core_metric_mmkt_ts_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.machine_id} {self.metric_key} {self.value}{self.unit}"
