from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import SiteConfiguration, BackgroundImage, MachineProduct, ShopProduct


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for site-wide settings (singleton).

    UX improvement:
    - If the singleton already exists, going to the changelist will jump straight
      to the edit page so you don't have to click the row.
    """

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
            "description": "Homepage hero image/text, call-to-action button, and the three feature bullets.",
        }),
        ("Contact Information", {
            "fields": ("phone_number", "email", "location"),
            "description": "Contact details shown throughout the site",
        }),
        ("Social Media", {
            "fields": ("linkedin_url", "facebook_url", "youtube_url"),
            "description": "Social media profile URLs",
        }),
    )

    def changelist_view(self, request, extra_context=None):
        """Redirect the changelist straight to the singleton edit page."""
        if SiteConfiguration.objects.exists():
            obj = SiteConfiguration.get_config()
            return redirect(
                reverse("admin:core_siteconfiguration_change", args=(obj.pk,))
            )
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        """Prevent creating more than one configuration instance"""
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting the configuration"""
        return False


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
