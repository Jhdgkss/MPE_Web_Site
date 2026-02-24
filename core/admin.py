from __future__ import annotations

from django import forms
from django.contrib import admin

from . import models


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

class ColorPickerAdminMixin:
    """Use native HTML color picker for any CharField that looks like a colour."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        name = db_field.name
        if name.endswith("_color") or name.endswith("_bg_color") or name.endswith("_text_color"):
            kwargs["widget"] = forms.TextInput(attrs={"type": "color"})
        # PDF config uses accent_color
        if name in {"accent_color"}:
            kwargs["widget"] = forms.TextInput(attrs={"type": "color"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# -----------------------------------------------------------------------------
# Site config / hero / backgrounds
# -----------------------------------------------------------------------------

@admin.register(models.SiteConfiguration)
class SiteConfigurationAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    # Keep it usable rather than hyper-perfect: group the biggest blocks.
    fieldsets = (
        ("Branding", {"fields": ("logo", "favicon")}),
        ("Contact", {"fields": ("phone_number", "email", "location")}),
        ("Social", {"fields": ("linkedin_url", "facebook_url", "youtube_url")}),
        ("Homepage features", {"fields": ("feature_1", "feature_2", "feature_3")}),
        ("Shop", {"fields": ("shop_show_prices",)}),
        (
            "Theme",
            {
                "fields": (
                    "site_bg_color",
                    "site_bg_image",
                    "site_text_color",
                    "primary_color",
                    "secondary_color",
                    "link_color",
                    "topbar_bg_color",
                    "topbar_text_color",
                    "header_bg_color",
                    "header_text_color",
                    "hero_bg_color",
                    "hero_text_color",
                    "hero_box_bg_color",
                    "hero_box_bg_opacity",
                    "section_alt_bg_color",
                    "machines_section_bg_color",
                    "machines_section_text_color",
                    "distributors_section_bg_color",
                    "distributors_section_text_color",
                    "card_bg_color",
                    "card_text_color",
                    "footer_bg_color",
                    "footer_text_color",
                    "footer_link_color",
                )
            },
        ),
        (
            "Nav button styling",
            {
                "fields": (
                    "nav_btn_bg_color",
                    "nav_btn_bg_opacity",
                    "nav_btn_text_color",
                    "nav_btn_border_color",
                    "nav_btn_border_opacity",
                    "nav_btn_bg_hover_color",
                    "nav_btn_bg_hover_opacity",
                    "nav_btn_text_hover_color",
                    "nav_btn_border_hover_color",
                    "nav_btn_border_hover_opacity",
                    "nav_btn_text_shadow",
                )
            },
        ),
        (
            "Page themes",
            {
                "fields": (
                    "contact_hero_bg_color",
                    "contact_hero_text_color",
                    "contact_section_bg_color",
                    "contact_section_text_color",
                    "shop_hero_bg_color",
                    "shop_hero_text_color",
                    "shop_section_bg_color",
                    "shop_section_text_color",
                    "documents_hero_bg_color",
                    "documents_hero_text_color",
                    "documents_section_bg_color",
                    "documents_section_text_color",
                    "tooling_hero_bg_color",
                    "tooling_hero_text_color",
                    "tooling_section_bg_color",
                    "tooling_section_text_color",
                    "tooling_section_heading_color",
                    "tooling_feature_bg_color",
                    "tooling_feature_text_color",
                    "portal_hero_bg_color",
                    "portal_hero_text_color",
                    "portal_section_bg_color",
                    "portal_section_text_color",
                )
            },
        ),
        ("Advanced", {"fields": ("custom_css",)}),
    )


@admin.register(models.HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "style", "is_active", "sort_order", "created_at")
    list_filter = ("style", "is_active")
    search_fields = ("title", "subtitle")
    ordering = ("sort_order", "created_at")


@admin.register(models.BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    # BackgroundImage model: title, image, is_active, created_at
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "image")
    ordering = ("-created_at",)


# -----------------------------------------------------------------------------
# Machine products
# -----------------------------------------------------------------------------

class MachineProductImageInline(admin.TabularInline):
    model = models.MachineProductImage
    extra = 0


class MachineProductDocumentInline(admin.TabularInline):
    model = models.MachineProductDocument
    extra = 0


class MachineProductVideoInline(admin.TabularInline):
    model = models.MachineProductVideo
    extra = 0


class MachineProductStatInline(admin.TabularInline):
    model = models.MachineProductStat
    extra = 0


class MachineProductFeatureInline(admin.TabularInline):
    model = models.MachineProductFeature
    extra = 0


@admin.register(models.MachineProduct)
class MachineProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "tagline", "is_active", "sort_order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "tagline", "description", "overview_body")
    ordering = ("sort_order", "name")
    inlines = (
        MachineProductImageInline,
        MachineProductDocumentInline,
        MachineProductVideoInline,
        MachineProductStatInline,
        MachineProductFeatureInline,
    )
    fieldsets = (
        ("Core", {"fields": ("name", "slug", "tagline", "description", "is_active", "sort_order")}),
        ("Hero", {"fields": ("hero_image", "hero_title", "hero_subtitle")}),
        ("Page content", {"fields": ("overview_title", "overview_body", "key_features")}),
        ("Listing media", {"fields": ("image", "spec_pdf", "external_link")}),
    )


# Optional: allow editing related models directly too
@admin.register(models.MachineProductImage)
class MachineProductImageAdmin(admin.ModelAdmin):
    list_display = ("machine", "caption", "sort_order")
    ordering = ("machine", "sort_order")


@admin.register(models.MachineProductDocument)
class MachineProductDocumentAdmin(admin.ModelAdmin):
    list_display = ("machine", "title", "sort_order")
    ordering = ("machine", "sort_order")


@admin.register(models.MachineProductVideo)
class MachineProductVideoAdmin(admin.ModelAdmin):
    list_display = ("machine", "title", "sort_order")
    ordering = ("machine", "sort_order")


@admin.register(models.MachineProductStat)
class MachineProductStatAdmin(admin.ModelAdmin):
    list_display = ("machine", "label", "value", "sort_order")
    ordering = ("machine", "sort_order")


@admin.register(models.MachineProductFeature)
class MachineProductFeatureAdmin(admin.ModelAdmin):
    list_display = ("machine", "title", "icon", "sort_order")
    ordering = ("machine", "sort_order")


# -----------------------------------------------------------------------------
# Shop
# -----------------------------------------------------------------------------

class ShopOrderItemInline(admin.TabularInline):
    model = models.ShopOrderItem
    extra = 0
    autocomplete_fields = ("product",)


@admin.register(models.ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "sku", "category", "price_gbp", "in_stock", "is_active", "sort_order")
    list_filter = ("category", "in_stock", "is_active", "show_price")
    search_fields = ("name", "sku", "description")
    ordering = ("sort_order", "name")


@admin.register(models.ShopOrder)
class ShopOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "order_number", "contact", "contact_email", "status", "created_at")
    list_filter = ("status", "created_at", "email_sent_to_customer", "email_sent_to_internal")
    search_fields = ("order_number", "contact__name", "contact__email", "contact__company")
    ordering = ("-created_at",)
    inlines = (ShopOrderItemInline,)

    @admin.display(description="Customer email")
    def contact_email(self, obj):
        return getattr(obj.contact, "email", "")


@admin.register(models.ShopOrderAddress)
class ShopOrderAddressAdmin(admin.ModelAdmin):
    list_display = ("order", "label", "city", "postcode", "country")
    list_filter = ("country",)
    search_fields = ("order__order_number", "label", "city", "postcode")


@admin.register(models.ShopOrderItem)
class ShopOrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "sku", "quantity", "unit_price_gbp")
    search_fields = ("order__order_number", "product_name", "sku")


# -----------------------------------------------------------------------------
# CRM / portal
# -----------------------------------------------------------------------------

@admin.register(models.CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "phone", "created_at")
    search_fields = ("name", "email", "company", "phone")
    ordering = ("-created_at",)


@admin.register(models.CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("contact", "label", "city", "postcode", "country", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("contact__name", "contact__email", "city", "postcode", "label")
    ordering = ("-is_default", "label")


@admin.register(models.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__username", "user__email", "company_name")


@admin.register(models.StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "level")
    list_filter = ("level",)
    search_fields = ("user__username", "user__email")


@admin.register(models.StaffDocument)
class StaffDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "uploaded_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "category")
    ordering = ("-uploaded_at",)


@admin.register(models.CustomerMachine)
class CustomerMachineAdmin(admin.ModelAdmin):
    list_display = ("customer", "name", "machine_type", "serial_number", "is_active")
    list_filter = ("machine_type", "is_active")
    search_fields = ("customer__username", "name", "serial_number")


@admin.register(models.CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "customer", "category", "is_active", "uploaded_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "customer__username")
    ordering = ("-uploaded_at",)


@admin.register(models.MachineMetric)
class MachineMetricAdmin(admin.ModelAdmin):
    list_display = ("machine", "metric_key", "value", "unit", "timestamp")
    list_filter = ("metric_key", "unit")
    search_fields = ("machine__name", "metric_key")
    ordering = ("-timestamp",)


@admin.register(models.MachineTelemetry)
class MachineTelemetryAdmin(admin.ModelAdmin):
    list_display = ("machine_id", "status", "ppm", "temp", "batch_count", "created_at")
    list_filter = ("status",)
    search_fields = ("machine_id",)
    ordering = ("-created_at",)


# -----------------------------------------------------------------------------
# Distribution
# -----------------------------------------------------------------------------

@admin.register(models.Distributor)
class DistributorAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    list_display = ("country_name", "flag_code", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("country_name", "flag_code", "description")
    ordering = ("sort_order", "country_name")


# -----------------------------------------------------------------------------
# PDF / Email config
# -----------------------------------------------------------------------------

@admin.register(models.PDFConfiguration)
class PDFConfigurationAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    list_display = ("company_name", "header_email", "header_phone", "document_title")


@admin.register(models.EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = ("from_email", "send_to_customer", "send_to_internal", "attach_order_pdf")


@admin.register(models.EmailSettings)
class EmailSettingsAdmin(EmailConfigurationAdmin):
    pass
