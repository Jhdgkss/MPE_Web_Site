from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db import connection

from .models import (
    SiteConfiguration, BackgroundImage, HeroSlide, MachineProduct, ShopProduct,
    CustomerProfile, CustomerMachine, CustomerDocument, StaffDocument, MachineMetric
)


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Logo & Branding", {"fields": ("logo",)}),
        ("Hero Section", {"fields": ("hero_title","hero_subtitle","hero_description","hero_image","hero_button_text","hero_button_link")}),
        ("Feature Bullets", {"fields": ("feature_1","feature_2","feature_3")}),
        ("Contact Information", {"fields": ("phone_number","email","location")}),
        ("Social Media", {"fields": ("linkedin_url","facebook_url","youtube_url")}),
    )

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
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


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("sort_order", "title", "kind", "is_active", "created_at")
    list_filter = ("is_active", "kind")
    search_fields = ("title", "subtitle", "body")
    ordering = ("sort_order", "created_at")


# -----------------------------------------------------------------------------
# Portal models
# -----------------------------------------------------------------------------

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("company_name", "user__username", "user__email")


@admin.register(CustomerMachine)
class CustomerMachineAdmin(admin.ModelAdmin):
    list_display = ("customer", "name", "machine_type", "serial_number", "is_active")
    list_filter = ("machine_type", "is_active")
    search_fields = ("customer__username", "name", "serial_number")


@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ("customer", "title", "category", "is_active", "uploaded_at")
    list_filter = ("category", "is_active")
    search_fields = ("customer__username", "title")


@admin.register(StaffDocument)
class StaffDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "uploaded_at")
    list_filter = ("category", "is_active")
    search_fields = ("title",)


@admin.register(MachineMetric)
class MachineMetricAdmin(admin.ModelAdmin):
    list_display = ("machine", "metric_key", "value", "unit", "timestamp")
    list_filter = ("metric_key",)
    search_fields = ("machine__name", "machine__serial_number", "metric_key")
    date_hierarchy = "timestamp"


# -----------------------------------------------------------------------------
# Make CustomerProfile editable on the User page, but don't crash if migrations
# haven't been applied yet.
# -----------------------------------------------------------------------------

User = get_user_model()

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = True
    extra = 0


def _table_exists(table_name: str) -> bool:
    try:
        return table_name in connection.introspection.table_names()
    except Exception:
        return False


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    def get_inline_instances(self, request, obj=None):
        inlines = []
        # Only show the inline once the DB table exists (after migrate)
        if _table_exists("core_customerprofile"):
            self.inlines = [CustomerProfileInline]
        else:
            self.inlines = []
        return super().get_inline_instances(request, obj)
