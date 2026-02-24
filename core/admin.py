from django.contrib import admin
from django import forms

from .models import (
    SiteConfiguration,
    HeroSlide,
    BackgroundImage,
    MachineProduct,
    MachineProductImage,
    MachineProductDocument,
    MachineProductVideo,
    MachineProductStat,
    MachineProductFeature,
    ShopProduct,
    CustomerContact,
    CustomerAddress,
    ShopOrder,
    ShopOrderAddress,
    ShopOrderItem,
    CustomerProfile,
    StaffProfile,
    StaffDocument,
    CustomerMachine,
    CustomerDocument,
    MachineMetric,
    MachineTelemetry,
    Distributor,
    PDFConfiguration,
    EmailConfiguration,
)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

class ColorPickerAdminMixin:
    """Render common hex colour fields using a native HTML colour picker."""

    COLOR_FIELD_SUFFIXES = ("_color", "_bg_color", "_text_color")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name.endswith(self.COLOR_FIELD_SUFFIXES) or db_field.name in {"image_frame_bg_color", "accent_color"}:
            kwargs.setdefault("widget", forms.TextInput(attrs={"type": "color"}))
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# -----------------------------------------------------------------------------
# Site / Theme
# -----------------------------------------------------------------------------

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    list_display = ("id", "phone_number", "email", "location", "shop_show_prices")

    def has_add_permission(self, request):
        # Keep SiteConfiguration as a singleton (one row).
        if SiteConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(HeroSlide)
class HeroSlideAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    list_display = ("id", "title", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")
    ordering = ("sort_order", "id")


@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("sort_order", "id")


# -----------------------------------------------------------------------------
# Machines
# -----------------------------------------------------------------------------

class MachineProductImageInline(admin.TabularInline):
    model = MachineProductImage
    extra = 0


class MachineProductDocumentInline(admin.TabularInline):
    model = MachineProductDocument
    extra = 0


class MachineProductVideoInline(admin.TabularInline):
    model = MachineProductVideo
    extra = 0


class MachineProductStatInline(admin.TabularInline):
    model = MachineProductStat
    extra = 0


class MachineProductFeatureInline(admin.TabularInline):
    model = MachineProductFeature
    extra = 0


@admin.register(MachineProduct)
class MachineProductAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "short_description", "long_description")
    ordering = ("sort_order", "name")
    inlines = [
        MachineProductImageInline,
        MachineProductDocumentInline,
        MachineProductVideoInline,
        MachineProductStatInline,
        MachineProductFeatureInline,
    ]


# -----------------------------------------------------------------------------
# Shop
# -----------------------------------------------------------------------------

@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "sku", "category", "price_gbp", "is_active", "sort_order", "in_stock")
    list_filter = ("is_active", "category", "in_stock")
    search_fields = ("name", "sku", "slug", "description")
    ordering = ("sort_order", "name")


class ShopOrderItemInline(admin.TabularInline):
    model = ShopOrderItem
    extra = 0
    autocomplete_fields = ("product",)


class ShopOrderAddressInline(admin.StackedInline):
    model = ShopOrderAddress
    extra = 0
    max_num = 1


@admin.register(ShopOrder)
class ShopOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "contact", "status", "order_number", "email_sent_to_customer", "email_sent_to_internal")
    list_filter = ("status", "created_at", "email_sent_to_customer", "email_sent_to_internal")
    search_fields = ("contact__name", "contact__company", "contact__email", "order_number", "notes")
    date_hierarchy = "created_at"
    inlines = [ShopOrderAddressInline, ShopOrderItemInline]


# -----------------------------------------------------------------------------
# Customers / Staff / Documents
# -----------------------------------------------------------------------------

@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company", "email", "phone", "created_at")
    search_fields = ("name", "company", "email", "phone")
    date_hierarchy = "created_at"


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("id", "contact", "label", "postcode", "country")
    search_fields = ("contact__name", "contact__company", "postcode", "country", "label")


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "company_name", "is_active")
    search_fields = ("user__username", "user__email", "company_name")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "level")
    search_fields = ("user__username", "user__email")
    list_filter = ("level",)


@admin.register(StaffDocument)
class StaffDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "uploaded_at")
    list_filter = ("category", "uploaded_at")
    search_fields = ("title", "description")
    date_hierarchy = "uploaded_at"


@admin.register(CustomerMachine)
class CustomerMachineAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "name", "machine_type", "serial_number", "is_active")
    list_filter = ("machine_type", "is_active")
    search_fields = ("customer__username", "name", "serial_number")


@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "title", "category", "uploaded_at")
    list_filter = ("category", "uploaded_at")
    search_fields = ("title", "description", "customer__username")
    date_hierarchy = "uploaded_at"


# -----------------------------------------------------------------------------
# Telemetry / Metrics
# -----------------------------------------------------------------------------

@admin.register(MachineMetric)
class MachineMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "machine", "metric_key", "value", "unit", "timestamp")
    search_fields = ("machine__name", "machine__serial_number", "metric_key", "unit")
    list_filter = ("metric_key",)
    date_hierarchy = "timestamp"


@admin.register(MachineTelemetry)
class MachineTelemetryAdmin(admin.ModelAdmin):
    list_display = ("id", "machine_id", "status", "ppm", "temp", "batch_count", "created_at")
    search_fields = ("machine_id", "status")
    list_filter = ("status", "created_at")
    date_hierarchy = "created_at"


# -----------------------------------------------------------------------------
# Distributors / PDF / Email Config
# -----------------------------------------------------------------------------

@admin.register(Distributor)
class DistributorAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    list_display = ("country_name", "flag_code", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("country_name", "flag_code")
    ordering = ("sort_order", "country_name")


@admin.register(PDFConfiguration)
class PDFConfigurationAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    list_display = ("id", "company_name", "document_title")
    search_fields = ("company_name", "header_email", "document_title")

    def has_add_permission(self, request):
        if PDFConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ("id", "from_email", "send_to_customer", "send_to_internal", "attach_order_pdf")
    search_fields = ("from_email", "reply_to_email", "internal_recipients")

    def has_add_permission(self, request):
        if EmailConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)
