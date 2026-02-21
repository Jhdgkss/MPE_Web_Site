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
    Controls Logos, Contact Info, and Global CSS Styling.
    """
    # -- BRANDING --
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    favicon = models.ImageField(upload_to="site/", blank=True, null=True, help_text="Small icon for browser tab")

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

    # -- SHOP --
    shop_show_prices = models.BooleanField(
        default=True,
        help_text="If disabled, prices are hidden across the shop and customers must request a quote.",
    )

    # =========================================================================
    #  THEME CONFIGURATION
    # =========================================================================

    # 1. Global / Body
    site_bg_color = models.CharField(max_length=32, default="#ffffff", help_text="Main page background color")
    site_bg_image = models.ImageField(upload_to="site/theme/", blank=True, null=True, help_text="Optional: Overrides background color")
    site_text_color = models.CharField(max_length=32, default="#333333", help_text="Main body text color")

    primary_color = models.CharField(max_length=32, default="#1f9d55", help_text="Primary Brand Color (Buttons, Highlights)")
    secondary_color = models.CharField(max_length=32, default="#0f172a", help_text="Secondary Brand Color (Dark backgrounds)")
    link_color = models.CharField(max_length=32, default="#1f9d55", help_text="Hyperlink text color")

    # 2. Layout Sections
    topbar_bg_color = models.CharField(max_length=32, default="#ffffff", help_text="Very top strip background")
    topbar_text_color = models.CharField(max_length=32, default="#333333")

    hero_bg_color = models.CharField(max_length=32, default="#001a4d", help_text="Hero/Banner background color")
    hero_text_color = models.CharField(max_length=32, default="#ffffff")

    # Hero Text Box Settings
    hero_box_bg_color = models.CharField(max_length=32, default="#001a4d", help_text="Background color of the text box over the image")
    hero_box_bg_opacity = models.PositiveSmallIntegerField(default=85, help_text="0-100% (0 is transparent, 100 is solid)")

    section_alt_bg_color = models.CharField(max_length=32, default="#f3f4f6", help_text="Background for alternating sections (stripes)")

    # 4. Section-specific styling (Machines + Distributors)
    machines_section_bg_color = models.CharField(max_length=32, default="#f3f4f6", help_text="Background for the 'Our Machinery Range' section")
    machines_section_text_color = models.CharField(max_length=32, default="#0b1220", help_text="Text color for the 'Our Machinery Range' section")

    distributors_section_bg_color = models.CharField(max_length=32, default="#0b1220", help_text="Background for the 'Global Distribution Network' section")
    distributors_section_text_color = models.CharField(max_length=32, default="#ffffff", help_text="Text color for the 'Global Distribution Network' section")

    card_bg_color = models.CharField(max_length=32, default="#ffffff", help_text="Background for boxes/cards")
    card_text_color = models.CharField(max_length=32, default="#333333")

    # 3. Header / Navbar
    header_bg_color = models.CharField(max_length=32, default="#ffffff")
    header_text_color = models.CharField(max_length=32, default="#0f172a")

    # 4. Footer
    footer_bg_color = models.CharField(max_length=32, default="#0f172a")
    footer_text_color = models.CharField(max_length=32, default="#ffffff")
    footer_link_color = models.CharField(max_length=32, default="#1f9d55")

    # 5. Navigation Buttons
    nav_btn_bg_color = models.CharField(max_length=32, default="#1f9d55", blank=True)
    nav_btn_bg_opacity = models.PositiveSmallIntegerField(default=14, help_text="0-100 (%)")
    nav_btn_text_color = models.CharField(max_length=32, default="#0f172a", blank=True)
    nav_btn_border_color = models.CharField(max_length=32, default="#1f9d55", blank=True)
    nav_btn_border_opacity = models.PositiveSmallIntegerField(default=25, help_text="0-100 (%)")

    nav_btn_bg_hover_color = models.CharField(max_length=32, default="#1f9d55", blank=True)
    nav_btn_bg_hover_opacity = models.PositiveSmallIntegerField(default=22, help_text="0-100 (%)")
    nav_btn_text_hover_color = models.CharField(max_length=32, default="#0b1220", blank=True)
    nav_btn_border_hover_color = models.CharField(max_length=32, default="#1f9d55", blank=True)
    nav_btn_border_hover_opacity = models.PositiveSmallIntegerField(default=38, help_text="0-100 (%)")
    nav_btn_text_shadow = models.CharField(max_length=64, default="0 1px 2px rgba(0,0,0,.25)", blank=True)

    # 7. Page Specific - Contact
    contact_hero_bg_color = models.CharField(max_length=32, default="#001a4d", help_text="Contact page hero background")
    contact_hero_text_color = models.CharField(max_length=32, default="#ffffff")
    contact_section_bg_color = models.CharField(max_length=32, default="#f3f4f6", help_text="Contact page main section background")
    contact_section_text_color = models.CharField(max_length=32, default="#333333")

    # 8. Page Specific - Shop
    shop_hero_bg_color = models.CharField(max_length=32, default="#001a4d")
    shop_hero_text_color = models.CharField(max_length=32, default="#ffffff")
    shop_section_bg_color = models.CharField(max_length=32, default="#f3f4f6")
    shop_section_text_color = models.CharField(max_length=32, default="#333333")

    # 9. Page Specific - Documents
    documents_hero_bg_color = models.CharField(max_length=32, default="#001a4d")
    documents_hero_text_color = models.CharField(max_length=32, default="#ffffff")
    documents_section_bg_color = models.CharField(max_length=32, default="#f3f4f6")
    documents_section_text_color = models.CharField(max_length=32, default="#333333")

    # 10. Page Specific - Tooling
    tooling_hero_bg_color = models.CharField(max_length=32, default="#001a4d")
    tooling_hero_text_color = models.CharField(max_length=32, default="#ffffff")
    tooling_section_bg_color = models.CharField(max_length=32, default="#f3f4f6")
    tooling_section_text_color = models.CharField(max_length=32, default="#333333")
    tooling_section_heading_color = models.CharField(max_length=32, default="#333333", help_text="Color for H2 headings")
    tooling_feature_bg_color = models.CharField(max_length=32, default="#ffffff", help_text="Background color for feature cards")
    tooling_feature_text_color = models.CharField(max_length=32, default="#333333", help_text="Text color for feature cards")

    # 11. Page Specific - Customer Portal
    portal_hero_bg_color = models.CharField(max_length=32, default="#001a4d")
    portal_hero_text_color = models.CharField(max_length=32, default="#ffffff")
    portal_section_bg_color = models.CharField(max_length=32, default="#f3f4f6")
    portal_section_text_color = models.CharField(max_length=32, default="#333333")

    # 6. Advanced / Custom CSS
    custom_css = models.TextField(blank=True, help_text="Global custom CSS applied to the whole site.")

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

    # ---- Helpers for Template Logic ----
    @staticmethod
    def _clamp_pct(value: int) -> int:
        try:
            v = int(value)
        except Exception:
            return 0
        return max(0, min(100, v))

    def rgba_from_hex(self, hex_color: str, opacity_pct: int) -> str:
        if not hex_color:
            return ""
        s = str(hex_color).strip()
        if not s.startswith("#"):
            return s
        s = s.lstrip("#")
        if len(s) == 3:
            s = "".join([c * 2 for c in s])
        if len(s) != 6:
            return "#" + s
        try:
            r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        except ValueError:
            return "#" + s
        a = self._clamp_pct(opacity_pct) / 100.0
        return f"rgba({r}, {g}, {b}, {a:.2f})"

    @property
    def nav_btn_bg_rgba(self):
        return self.rgba_from_hex(self.nav_btn_bg_color, self.nav_btn_bg_opacity)

    @property
    def nav_btn_border_rgba(self):
        return self.rgba_from_hex(self.nav_btn_border_color, self.nav_btn_border_opacity)

    @property
    def nav_btn_bg_hover_rgba(self):
        return self.rgba_from_hex(self.nav_btn_bg_hover_color, self.nav_btn_bg_hover_opacity)

    @property
    def nav_btn_border_hover_rgba(self):
        return self.rgba_from_hex(self.nav_btn_border_hover_color, self.nav_btn_border_hover_opacity)

    @property
    def hero_box_bg_rgba(self):
        return self.rgba_from_hex(self.hero_box_bg_color, self.hero_box_bg_opacity)


# -----------------------------------------------------------------------------
# 2. Hero Slides
# -----------------------------------------------------------------------------
class HeroSlide(models.Model):
    STYLE_MACHINE = "machine"
    STYLE_NEWS = "news"
    STYLE_CHOICES = [(STYLE_MACHINE, "Machine Showcase"), (STYLE_NEWS, "News / Update")]

    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default=STYLE_MACHINE)
    title = models.CharField(max_length=120, help_text="Main heading or Machine Name")
    subtitle = models.CharField(max_length=180, blank=True, help_text="Tagline or short subtitle")
    description = models.TextField(blank=True, help_text="Paragraph text")

    image = models.ImageField(upload_to="hero_slides/", blank=True, null=True, help_text="Foreground image (machine cutout)")
    video = models.FileField(upload_to="hero_videos/", blank=True, null=True, help_text="Foreground video (machine running)")

    bg_image = models.ImageField(upload_to="hero_bgs_full/", blank=True, null=True, help_text="Full screen background image")
    bg_video = models.FileField(upload_to="hero_bg_videos/", blank=True, null=True, help_text="Full screen background video (MP4)")

    bg_color = models.CharField(max_length=32, blank=True, help_text="Optional: Solid background color if no image/video is uploaded.")
    bg_overlay_opacity = models.PositiveSmallIntegerField(default=50, help_text="Darkness of the overlay (0-100%). Higher = darker background.")

    card_background = models.ImageField(upload_to="hero_bgs/", blank=True, null=True, help_text="Optional: Texture for the specific content box.")
    transparent_background = models.BooleanField(default=False, help_text="Check this to make the content box transparent (good for 'See More' style slides).")

    cta_text = models.CharField(max_length=50, blank=True, default="View Details")
    cta_link = models.CharField(max_length=240, blank=True, help_text="Internal path or full URL")

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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or self.image.name


class MachineProduct(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(
        max_length=160,
        unique=True,
        blank=True,
        help_text="SEO-friendly URL slug (auto-generated if blank)",
    )
    tagline = models.CharField(max_length=180, blank=True)
    description = models.TextField(blank=True)

    # Optional: richer per-machine page content
    hero_image = models.ImageField(upload_to="machines/hero/", blank=True, null=True)
    image_frame_bg_color = models.CharField(max_length=32, blank=True, default="", help_text="Background colour for the machine image frame (e.g. #ffffff). Leave blank to use default.")
    hero_title = models.CharField(max_length=140, blank=True, default="")
    hero_subtitle = models.CharField(max_length=220, blank=True, default="")
    overview_title = models.CharField(max_length=140, blank=True, default="Overview")
    overview_body = models.TextField(blank=True, help_text="Main body text for the machine page")
    key_features = models.TextField(
        blank=True,
        help_text="One feature per line (we will display these as bullet points)",
    )
    image = models.ImageField(upload_to="machines/", blank=True, null=True)
    spec_pdf = models.FileField(upload_to="spec_sheets/", blank=True, null=True)
    external_link = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from django.utils.text import slugify

        if not self.slug:
            base = slugify(self.name)[:150] or "machine"
            slug = base
            i = 2
            while MachineProduct.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("machine_detail", kwargs={"slug": self.slug})


class MachineProductImage(models.Model):
    machine = models.ForeignKey(
        MachineProduct,
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )
    image = models.ImageField(upload_to="machines/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.machine.name} image"


class MachineProductDocument(models.Model):
    machine = models.ForeignKey(
        MachineProduct,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title = models.CharField(max_length=140)
    file = models.FileField(upload_to="machines/documents/", blank=True, null=True)
    url = models.URLField(blank=True, help_text="Optional external link instead of uploading a file")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return f"{self.machine.name}: {self.title}"

    @property
    def link(self):
        if self.file:
            return self.file.url
        return self.url


class MachineProductVideo(models.Model):
    machine = models.ForeignKey(
        MachineProduct,
        on_delete=models.CASCADE,
        related_name="videos",
    )
    title = models.CharField(max_length=140, blank=True, default="")
    video_url = models.URLField(
        blank=True,
        default="",
        help_text="YouTube/Vimeo (watch link) or any external video URL",
    )
    embed_url = models.URLField(
        blank=True,
        default="",
        help_text="Optional: paste an embed URL (if blank we auto-generate from video_url where possible).",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.machine.name} video"

    def _compute_embed_url(self) -> str:
        u = (self.video_url or "").strip()
        if "youtube.com/watch" in u and "v=" in u:
            vid = u.split("v=", 1)[1].split("&", 1)[0]
            return f"https://www.youtube.com/embed/{vid}"
        if "youtu.be/" in u:
            vid = u.split("youtu.be/", 1)[1].split("?", 1)[0].split("&", 1)[0]
            return f"https://www.youtube.com/embed/{vid}"
        if "vimeo.com/" in u:
            vid = u.rstrip("/").split("/")[-1]
            if vid.isdigit():
                return f"https://player.vimeo.com/video/{vid}"
        return u

    def save(self, *args, **kwargs):
        # If embed_url wasn't supplied, try to derive it from video_url.
        if not self.embed_url and self.video_url:
            self.embed_url = self._compute_embed_url()
        super().save(*args, **kwargs)


class MachineProductStat(models.Model):
    """Big number KPI/stat shown on a machine product page (per machine)."""
    machine = models.ForeignKey(
        MachineProduct,
        on_delete=models.CASCADE,
        related_name="stats",
    )
    value = models.CharField(max_length=32, help_text="e.g. 120, 50+, 24/7")
    label = models.CharField(max_length=80, help_text="e.g. Packs per minute")
    unit = models.CharField(max_length=32, blank=True, help_text="Optional unit, e.g. ppm")
    sort_order = models.PositiveIntegerField(default=0)
    is_highlight = models.BooleanField(default=False, help_text="If enabled, this stat may be styled more prominently")

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.machine.name}: {self.value} {self.label}"


class MachineProductFeature(models.Model):
    """Icon + short text feature, designed to draw attention (per machine)."""
    ICON_SPEED = "speed"
    ICON_TOOLING = "tooling"
    ICON_ELECTRIC = "electric"
    ICON_BUILD = "build"
    ICON_HYGIENE = "hygiene"
    ICON_SUPPORT = "support"
    ICON_MAP = "map"
    ICON_CUSTOM = "custom"

    ICON_CHOICES = [
        (ICON_SPEED, "Speed / Throughput"),
        (ICON_TOOLING, "Tooling / Changeover"),
        (ICON_ELECTRIC, "All-electric / Heat"),
        (ICON_BUILD, "Industrial build"),
        (ICON_HYGIENE, "Hygienic design"),
        (ICON_SUPPORT, "Service support"),
        (ICON_MAP, "MAP / Gas"),
        (ICON_CUSTOM, "Custom feature"),
    ]

    machine = models.ForeignKey(
        MachineProduct,
        on_delete=models.CASCADE,
        related_name="features",
    )
    icon = models.CharField(max_length=32, choices=ICON_CHOICES, default=ICON_SPEED)
    title = models.CharField(max_length=60, help_text="Short feature name, e.g. Speed")
    short_text = models.CharField(max_length=120, help_text="e.g. Up to 120 packs/min")
    sort_order = models.PositiveIntegerField(default=0)
    is_highlight = models.BooleanField(default=False, help_text="If enabled, this feature may be styled more prominently")

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.machine.name}: {self.title}"

    @property
    def icon_class(self) -> str:
        # Uses Font Awesome Free (solid) classes - adjust if your site uses different icon set
        return {
            self.ICON_SPEED: "fa-solid fa-gauge-high",
            self.ICON_TOOLING: "fa-solid fa-screwdriver-wrench",
            self.ICON_ELECTRIC: "fa-solid fa-bolt",
            self.ICON_BUILD: "fa-solid fa-industry",
            self.ICON_HYGIENE: "fa-solid fa-shield-halved",
            self.ICON_SUPPORT: "fa-solid fa-headset",
            self.ICON_MAP: "fa-solid fa-wind",
            self.ICON_CUSTOM: "fa-solid fa-star",
        }.get(self.icon, "fa-solid fa-star")
class ShopProduct(models.Model):
    CATEGORY_CHOICES = [
        ("parts", "Parts"),
        ("consumables", "Consumables"),
        ("accessories", "Accessories"),
        ("tooling", "Tooling"),
    ]

    name = models.CharField(max_length=140)
    slug = models.SlugField(
        max_length=160,
        unique=True,
        blank=True,
        help_text="SEO-friendly URL slug (auto-generated if blank)",
    )
    sku = models.CharField(max_length=60, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="parts")
    description = models.TextField(blank=True)

    show_price = models.BooleanField(
        default=True,
        help_text="If unchecked, the price is hidden for this product.",
    )
    price_gbp = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    specifications = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        help_text="Key/value specs shown on the product page (e.g. {'Voltage':'230V','Material':'Stainless'})",
    )

    image = models.ImageField(upload_to="shop/", blank=True, null=True)
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        from django.utils.text import slugify

        if not self.slug:
            base = slugify(self.name)[:150] or "product"
            slug = base
            i = 2
            while ShopProduct.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)


class CustomerContact(models.Model):
    """Reusable contact record for checkout + enquiries."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_contacts",
    )
    name = models.CharField(max_length=140)
    company = models.CharField(max_length=180, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    email = models.EmailField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["company", "name"]

    def __str__(self):
        return f"{self.company} - {self.name}" if self.company else self.name


class CustomerAddress(models.Model):
    contact = models.ForeignKey(CustomerContact, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=80, blank=True, help_text="e.g. Delivery, Head Office")

    address_1 = models.CharField(max_length=200)
    address_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=120, blank=True)
    county = models.CharField(max_length=120, blank=True)
    postcode = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=80, blank=True, default="United Kingdom")

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "label", "postcode"]

    def __str__(self):
        bits = [self.label or "Address", self.postcode or ""]
        return " ".join([b for b in bits if b]).strip()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            CustomerAddress.objects.filter(contact=self.contact).exclude(pk=self.pk).update(is_default=False)


class ShopOrder(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("viewed", "Viewed"),
        ("processing", "Processing"),
        ("complete", "Complete"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shop_orders",
    )
    contact = models.ForeignKey(CustomerContact, on_delete=models.PROTECT, related_name="orders")

    order_number = models.CharField(
        max_length=80,
        blank=True,
        help_text="Customer's internal order/reference number",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    notes = models.TextField(blank=True)

    # Email delivery tracking (helps diagnose SMTP vs. website issues)
    email_sent_to_customer = models.BooleanField(default=False)
    email_sent_to_internal = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(blank=True, null=True)
    email_last_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} ({self.contact})"


class ShopOrderAddress(models.Model):
    order = models.ForeignKey(ShopOrder, on_delete=models.CASCADE, related_name="order_addresses")

    label = models.CharField(max_length=80, blank=True)
    address_1 = models.CharField(max_length=200)
    address_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=120, blank=True)
    county = models.CharField(max_length=120, blank=True)
    postcode = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=80, blank=True, default="United Kingdom")

    def __str__(self):
        return f"{self.label or 'Address'} ({self.postcode})"


class ShopOrderItem(models.Model):
    order = models.ForeignKey(ShopOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ShopProduct, on_delete=models.SET_NULL, null=True, blank=True)

    product_name = models.CharField(max_length=160)
    sku = models.CharField(max_length=60, blank=True)
    unit_price_gbp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def line_total(self):
        return self.unit_price_gbp * self.quantity


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")
    company_name = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["company_name", "user__username"]

    def __str__(self):
        return self.company_name or self.user.get_username()


class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_profile")
    LEVEL_CHOICES = [
        (1, "Level 1 - Docs & Forms"),
        (2, "Level 2 - Orders"),
        (3, "Level 3 - Admin"),
    ]
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=1)

    def __str__(self):
        return f"{self.user.username} - Level {self.level}"


class StaffDocument(models.Model):
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, default="general")
    file = models.FileField(upload_to="staff_docs/")
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CustomerMachine(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_machines")
    name = models.CharField(max_length=140)
    machine_type = models.CharField(max_length=30, default="tray_sealer")
    serial_number = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class CustomerDocument(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_documents")
    title = models.CharField(max_length=160)
    category = models.CharField(max_length=20, default="general")
    file = models.FileField(upload_to="customer_docs/")
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class MachineMetric(models.Model):
    machine = models.ForeignKey("core.CustomerMachine", on_delete=models.CASCADE, related_name="metrics")
    metric_key = models.CharField(max_length=80)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]


class MachineTelemetry(models.Model):
    machine_id = models.CharField(max_length=50)
    ppm = models.FloatField()
    temp = models.FloatField()
    batch_count = models.IntegerField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.machine_id} - {self.created_at}"


class Distributor(models.Model):
    country_name = models.CharField(max_length=100)
    flag_code = models.CharField(max_length=5)
    description = models.TextField()
    cta_link = models.CharField(max_length=200)

    bg_color = models.CharField(max_length=32, blank=True, help_text="Optional background color")
    text_color = models.CharField(max_length=32, blank=True, help_text="Optional text color")
    border_color = models.CharField(max_length=32, blank=True, help_text="Optional border color")
    description_color = models.CharField(max_length=32, blank=True, help_text="Optional description text color")
    btn_bg_color = models.CharField(max_length=32, blank=True, help_text="Optional button background color")
    btn_text_color = models.CharField(max_length=32, blank=True, help_text="Optional button text color")

    logo = models.ImageField(upload_to="distributors/", blank=True, null=True, help_text="Optional logo to replace flag")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.country_name


# -----------------------------------------------------------------------------
# Email configuration (transactional emails)
# -----------------------------------------------------------------------------


class PDFConfiguration(models.Model):
    """Singleton config for generated PDFs (order summaries, etc.)."""

    pdf_logo = models.ImageField(
        upload_to="site/pdf/",
        blank=True,
        null=True,
        help_text="Logo used in generated PDFs (e.g. Order Summary).",
    )
    company_name = models.CharField(max_length=100, default="MPE UK Ltd", blank=True)
    header_email = models.EmailField(default="sales@mpe-uk.com", blank=True)
    header_phone = models.CharField(max_length=50, default="+44 1663 732700", blank=True)
    header_location = models.CharField(
        max_length=150,
        default="Unit 1, Bowden Lane, Derbyshire, SK23 0DQ",
        blank=True,
    )
    document_title = models.CharField(max_length=60, default="Order Summary", blank=True)
    accent_color = models.CharField(
        max_length=7,
        default="#2E7D32",
        blank=True,
        help_text="Header accent colour (hex), e.g. #2E7D32",
    )
    footer_text = models.CharField(max_length=200, default="Generated by MPE Web Site", blank=True)
    show_page_numbers = models.BooleanField(default=True)

    class Meta:
        verbose_name = "PDF configuration"
        verbose_name_plural = "PDF configurations"

    def __str__(self):
        return "PDF configuration"

    @classmethod
    def get_config(cls):
        cfg, _ = cls.objects.get_or_create(pk=1)
        return cfg


class EmailConfiguration(models.Model):
    """Singleton config for transactional emails (order confirmations, etc.)."""

    from_email = models.EmailField(default="sales@mpe-uk.com", blank=True)
    reply_to_email = models.EmailField(default="sales@mpe-uk.com", blank=True)

    # One per line or comma-separated
    internal_recipients = models.TextField(
        blank=True,
        default="sales@mpe-uk.com\nservice@mpe-uk.com\naccounts@mpe-uk.com",
        help_text="Internal recipients (one per line or comma-separated).",
    )

    send_to_customer = models.BooleanField(default=True)
    send_to_internal = models.BooleanField(default=True)

    attach_order_pdf = models.BooleanField(default=True)
    pdf_filename_template = models.CharField(
        max_length=200,
        default="Order_{order_id}.pdf",
        help_text="Attachment filename template. Available: {order_id}, {order_number}",
        blank=True,
    )

    customer_subject_template = models.CharField(
        max_length=200,
        default="Your order from MPE UK Ltd (Ref {order_ref})",
        blank=True,
    )
    internal_subject_template = models.CharField(
        max_length=200,
        default="New website order received (Ref {order_ref})",
        blank=True,
    )

    footer_note = models.CharField(
        max_length=300,
        default="MPE UK Ltd | Unit 1, Bowden Lane, Derbyshire, SK23 0DQ | +44 1663 732700",
        blank=True,
    )

    class Meta:
        verbose_name = "Email configuration"
        verbose_name_plural = "Email configurations"

    def __str__(self):
        return "Email configuration"

    @classmethod
    def get_config(cls):
        cfg, _ = cls.objects.get_or_create(pk=1)
        return cfg

    def parsed_internal_recipients(self):
        raw = (self.internal_recipients or "").replace(",", "\n")
        emails = [e.strip() for e in raw.splitlines() if e.strip()]
        # de-dup while preserving order
        seen=set(); out=[]
        for e in emails:
            if e.lower() in seen:
                continue
            seen.add(e.lower()); out.append(e)
        return out


class EmailSettings(EmailConfiguration):
    """Proxy model to show EmailConfiguration under an 'Emails' admin section."""

    class Meta:
        proxy = True
        verbose_name = "Email settings"
        verbose_name_plural = "Emails"
        app_label = "emails"
