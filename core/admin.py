from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import (
    SiteConfiguration,
    BackgroundImage,
    MachineProduct,
    ShopProduct,
    CustomerDocument,
    CustomerMachine,
    MachineMetric,
    StaffDocument,
)


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for site-wide settings (singleton)."""

    fieldsets = (
        ("Home Page", {
            "fields": (
                "logo",
                "hero_title",
                "hero_subtitle",
                "hero_description",
                "hero_image",
                "hero_button_text",
                "hero_button_link",
                "feature_1",
                "feature_2",
                "feature_3",
            ),
            "description": "Hero + homepage content (and the site logo).",
        }),
        ("Contact Information", {
            "fields": ("phone_number", "email", "location"),
        }),
        ("Social Media", {
            "fields": ("linkedin_url", "facebook_url", "youtube_url"),
        }),
    )

    def has_add_permission(self, request):
        # Prevent creating more than one configuration instance
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """If there is only one config row, jump straight into it."""
        qs = self.get_queryset(request)
        if qs.count() == 1:
            obj = qs.first()
            return redirect(reverse("admin:core_siteconfiguration_change", args=[obj.pk]))
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "image")


@admin.register(MachineProduct)
class MachineProductAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "tagline", "description")
    ordering = ("sort_order", "name")


@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_gbp", "in_stock", "is_active", "sort_order")
    list_filter = ("category", "in_stock", "is_active")
    search_fields = ("name", "sku", "description")
    ordering = ("sort_order", "name")
    list_editable = ("price_gbp", "in_stock", "is_active", "sort_order")


@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "customer", "category", "is_active", "uploaded_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "customer__username", "customer__email")
    ordering = ("-uploaded_at",)


@admin.register(CustomerMachine)
class CustomerMachineAdmin(admin.ModelAdmin):
    list_display = ("name", "customer", "machine_type", "serial_number", "is_active")
    list_filter = ("machine_type", "is_active")
    search_fields = ("name", "serial_number", "customer__username", "customer__email")
    ordering = ("customer", "name")


@admin.register(MachineMetric)
class MachineMetricAdmin(admin.ModelAdmin):
    list_display = ("machine", "metric_key", "value", "unit", "timestamp")
    list_filter = ("metric_key", "unit")
    search_fields = ("machine__name", "machine__serial_number", "metric_key")
    ordering = ("-timestamp",)


@admin.register(StaffDocument)
class StaffDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "uploaded_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "category")
    ordering = ("-uploaded_at",)
