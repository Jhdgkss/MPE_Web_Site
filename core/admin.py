from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db import connection

from .models import (
    SiteConfiguration, BackgroundImage, HeroSlide, MachineProduct, ShopProduct,
    CustomerProfile, CustomerMachine, CustomerDocument, StaffDocument, 
    MachineMetric, MachineTelemetry, Distributor # <--- Added Distributor
)

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Logo & Branding", {"fields": ("logo",)}),
        ("Contact Information", {"fields": ("phone_number","email","location")}),
        ("Social Media", {"fields": ("linkedin_url","facebook_url","youtube_url")}),
        ("Global Features", {"fields": ("feature_1","feature_2","feature_3")}),
    )
    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "style", "sort_order", "is_active", "created_at")
    list_filter = ("style", "is_active")
    search_fields = ("title", "subtitle")
    ordering = ("sort_order", "created_at")
    fieldsets = (
        ("Slide Type", {"fields": ("style", "is_active", "sort_order")}),
        ("Content", {"fields": ("title", "subtitle", "description")}),
        ("Media Content", {"fields": ("image", "video")}),
        ("Media Background", {
            "fields": ("card_background", "transparent_background"),
            "description": "Customize the box behind the machine image."
        }),
        ("Call To Action", {"fields": ("cta_text", "cta_link")}),
        ("Settings", {"fields": ("show_features",)}),
    )

# --- NEW: Distributor Admin ---
@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ("country_name", "flag_code", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("country_name", "description")
    help_text = "Use lowercase country codes for flags (gb, us, ca, fr, de, etc)."

# --- Existing Admins ---
@admin.register(BackgroundImage)
class BackgroundImageAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")

@admin.register(MachineProduct)
class MachineProductAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "sort_order")

@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "in_stock")

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "user")

@admin.register(CustomerMachine)
class CustomerMachineAdmin(admin.ModelAdmin):
    list_display = ("customer", "name")

@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ("customer", "title")

@admin.register(StaffDocument)
class StaffDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category")

@admin.register(MachineTelemetry)
class MachineTelemetryAdmin(admin.ModelAdmin):
    list_display = ("machine_id", "status", "ppm", "created_at")

# --- User Admin ---
User = get_user_model()
class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = True
    extra = 0

def _table_exists(table_name: str) -> bool:
    try: return table_name in connection.introspection.table_names()
    except: return False

try: admin.site.unregister(User)
except: pass

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    def get_inline_instances(self, request, obj=None):
        if _table_exists("core_customerprofile"):
            self.inlines = [CustomerProfileInline]
        else:
            self.inlines = []
        return super().get_inline_instances(request, obj)