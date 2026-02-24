"""Django admin configuration for the `core` app.

This file is intentionally defensive:
- It registers all models defined in core.models.
- It uses fieldsets and collapsible sections to keep large models manageable.
- It applies HTML colour pickers to common *_color fields (and a few other known
  colour-like CharFields) without requiring any third-party admin skin.
"""

from __future__ import annotations

from django import forms
from django.contrib import admin

from . import models


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _is_color_field(field_name: str) -> bool:
    """Heuristic to decide whether a CharField should use an HTML colour picker."""
    n = (field_name or "").lower()
    if not n:
        return False
    if n.endswith("_color"):
        return True
    if n.endswith("_colour"):
        return True
    return False


class ColorPickerAdminMixin:
    """Adds <input type=color> widgets for common colour fields."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):  # type: ignore[override]
        if getattr(db_field, "name", None):
            name = str(db_field.name)

            if _is_color_field(name) or name == "image_frame_bg_color":
                kwargs.setdefault(
                    "widget",
                    forms.TextInput(
                        attrs={
                            "type": "color",
                            "style": "width: 4.2rem; height: 2.2rem; padding: 0;",
                        }
                    ),
                )

        return super().formfield_for_dbfield(db_field, request, **kwargs)


# -----------------------------------------------------------------------------
# Inlines
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


class ShopOrderItemInline(admin.TabularInline):
    model = models.ShopOrderItem
    extra = 0
    readonly_fields = ("product", "qty", "unit_price_gbp", "line_total_gbp")
    fields = ("product", "qty", "unit_price_gbp", "line_total_gbp")
    can_delete = False


class ShopOrderAddressInline(admin.StackedInline):
    model = models.ShopOrderAddress
    extra = 0
    max_num = 1


# -----------------------------------------------------------------------------
# Model admins
# -----------------------------------------------------------------------------


@admin.register(models.SiteConfiguration)
class SiteConfigurationAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    """Singleton: keep the admin form tidy."""

    fieldsets = (
        (
            "Branding",
            {"fields": ("logo", "favicon")},
        ),
        (
            "Contact",
            {"fields": ("phone_number", "email", "location")},
        ),
        (
            "Social",
            {
                "classes": ("collapse",),
                "fields": ("linkedin_url", "facebook_url", "youtube_url"),
            },
        ),
        (
            "Homepage Features",
            {"fields": ("feature_1", "feature_2", "feature_3")},
        ),
        (
            "Shop",
            {"fields": ("shop_show_prices",)},
        ),
        (
            "Theme: Global",
            {
                "fields": (
                    ("site_bg_color", "site_text_color"),
                    "site_bg_image",
                    ("primary_color", "secondary_color", "link_color"),
                    ("card_bg_color", "card_text_color"),
                    ("section_alt_bg_color",),
                )
            },
        ),
        (
            "Theme: Header / Topbar / Footer",
            {
                "classes": ("collapse",),
                "fields": (
                    ("topbar_bg_color", "topbar_text_color"),
                    ("header_bg_color", "header_text_color"),
                    ("footer_bg_color", "footer_text_color", "footer_link_color"),
                ),
            },
        ),
        (
            "Theme: Hero",
            {
                "classes": ("collapse",),
                "fields": (
                    ("hero_bg_color", "hero_text_color"),
                    ("hero_box_bg_color", "hero_box_bg_opacity"),
                ),
            },
        ),
        (
            "Theme: Navigation Buttons",
            {
                "classes": ("collapse",),
                "fields": (
                    ("nav_btn_bg_color", "nav_btn_bg_opacity"),
                    ("nav_btn_text_color", "nav_btn_border_color", "nav_btn_border_opacity"),
                    ("nav_btn_bg_hover_color", "nav_btn_bg_hover_opacity"),
                    ("nav_btn_text_hover_color", "nav_btn_border_hover_color", "nav_btn_border_hover_opacity"),
                    ("nav_btn_text_shadow",),
                ),
            },
        ),
        (
            "Theme: Section Overrides",
            {
                "classes": ("collapse",),
                "fields": (
                    ("machines_section_bg_color", "machines_section_text_color"),
                    ("distributors_section_bg_color", "distributors_section_text_color"),
                ),
            },
        ),
        (
            "Theme: Page Overrides",
            {
                "classes": ("collapse",),
                "fields": (
                    ("contact_hero_bg_color", "contact_hero_text_color"),
                    ("contact_section_bg_color", "contact_section_text_color"),
                    ("shop_hero_bg_color", "shop_hero_text_color"),
                    ("shop_section_bg_color", "shop_section_text_color"),
                    ("documents_hero_bg_color", "documents_hero_text_color"),
                    ("documents_section_bg_color", "documents_section_text_color"),
                    ("tooling_hero_bg_color", "tooling_hero_text_color"),
                    ("tooling_section_bg_color", "tooling_section_text_color"),
                    ("tooling_section_heading_color",),
                    ("tooling_feature_bg_color", "tooling_feature_text_color"),
                    ("portal_hero_bg_color", "portal_hero_text_color"),
                    ("portal_section_bg_color", "portal_section_text_color"),
                ),
            },
        ),
        (
            "Advanced: Custom CSS",
            {
                "classes": ("collapse",),
                "fields": ("custom_css",),
            },
        ),
    )


@admin.register(models.HeroSlide)
class HeroSlideAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    list_display = ("title", "style", "is_active", "created_at")
    list_filter = ("style", "is_active")
    search_fields = ("title", "subtitle")


@admin.register(models.BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title",)
    ordering = ("-created_at",)


@admin.register(models.MachineProduct)
class MachineProductAdmin(ColorPickerAdminMixin, admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "category", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("name", "short_description", "description")
    inlines = (
        MachineProductImageInline,
        MachineProductDocumentInline,
        MachineProductVideoInline,
        MachineProductStatInline,
        MachineProductFeatureInline,
    )

    fieldsets = (
        (
            "Basics",
            {
                "fields": (
                    ("name", "slug"),
                    ("category", "is_active"),
                    "hero_heading",
                    "short_description",
                    "description",
                )
            },
        ),
        (
            "Hero / Card Media",
            {"fields": ("image", "hero_image", "image_frame_bg_color")},
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("meta_title", "meta_description"),
            },
        ),
        (
            "Advanced",
            {
                "classes": ("collapse",),
                "fields": ("sort_order",),
            },
        ),
    )


@admin.register(models.ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "sku", "is_active", "show_price", "price_gbp")
    list_filter = ("is_active", "show_price")
    search_fields = ("name", "sku", "description")
    ordering = ("name",)


@admin.register(models.ShopOrder)
class ShopOrderAdmin(admin.ModelAdmin):
    list_display = ("created_at", "customer_name", "status", "total_gbp", "email")
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "email", "po_number", "reference")
    readonly_fields = ("created_at", "updated_at", "total_gbp", "pdf_file", "pdf_filename")
    inlines = (ShopOrderAddressInline, ShopOrderItemInline)


@admin.register(models.CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "email", "created_at")
    search_fields = ("name", "company", "email", "message")
    list_filter = ("created_at",)


@admin.register(models.CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "city", "country", "created_at")
    search_fields = ("name", "company", "city", "postcode")
    list_filter = ("country",)


@admin.register(models.CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "phone")
    search_fields = ("user__username", "user__email", "company")


@admin.register(models.StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_active")
    list_filter = ("is_active", "role")
    search_fields = ("user__username", "user__email")


@admin.register(models.StaffDocument)
class StaffDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "uploaded_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "description")


@admin.register(models.CustomerMachine)
class CustomerMachineAdmin(admin.ModelAdmin):
    list_display = ("customer", "machine_name", "serial_number", "installed_date")
    search_fields = ("customer__user__username", "machine_name", "serial_number")
    list_filter = ("installed_date",)


@admin.register(models.CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ("customer", "title", "category", "uploaded_at")
    search_fields = ("title", "customer__user__username")
    list_filter = ("category",)


@admin.register(models.MachineMetric)
class MachineMetricAdmin(admin.ModelAdmin):
    list_display = ("machine", "name", "unit", "created_at")
    search_fields = ("machine__machine_name", "name")
    list_filter = ("created_at",)


@admin.register(models.MachineTelemetry)
class MachineTelemetryAdmin(admin.ModelAdmin):
    list_display = ("machine", "metric", "value", "timestamp")
    search_fields = ("machine__machine_name", "metric__name")
    list_filter = ("timestamp",)


@admin.register(models.Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "is_active")
    list_filter = ("region", "is_active")
    search_fields = ("name", "region")


@admin.register(models.PDFConfiguration)
class PDFConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Branding", {"fields": ("company_name", "company_address", "logo")}),
        ("Invoice / Order", {"fields": ("invoice_title", "terms_and_conditions")}),
    )


@admin.register(models.EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Routing", {"fields": ("from_email", "sales_team_email")}),
        (
            "Templates",
            {
                "classes": ("collapse",),
                "fields": (
                    "customer_subject",
                    "customer_body",
                    "sales_subject",
                    "sales_body",
                ),
            },
        ),
    )


@admin.register(models.EmailSettings)
class EmailSettingsAdmin(EmailConfigurationAdmin):
    """Proxy for EmailConfiguration to show up with a nicer label."""

    pass
