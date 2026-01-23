from django.contrib import admin
from .models import SiteConfiguration, BackgroundImage, MachineProduct, ShopProduct


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for site-wide settings"""
    
    fieldsets = (
        ("Logo & Branding", {
            "fields": ("logo",),
            "description": "Upload your site logo (PNG recommended with transparent background)"
        }),
        ("Hero Section", {
            "fields": (
                "hero_title",
                "hero_subtitle", 
                "hero_description",
                "hero_image",
                "hero_button_text",
                "hero_button_link"
            ),
            "description": "Configure the main hero/showcase section on the homepage"
        }),
        ("Feature Bullets", {
            "fields": ("feature_1", "feature_2", "feature_3"),
            "description": "Three key features displayed in the hero section"
        }),
        ("Contact Information", {
            "fields": ("phone_number", "email", "location"),
            "description": "Contact details shown throughout the site"
        }),
        ("Social Media", {
            "fields": ("linkedin_url", "facebook_url", "youtube_url"),
            "description": "Social media profile URLs"
        }),
    )
    
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
