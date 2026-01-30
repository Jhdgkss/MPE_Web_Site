from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db import connection
from import_export import resources 
from import_export.admin import ImportExportModelAdmin

from .models import (
    SiteConfiguration, BackgroundImage, HeroSlide, MachineProduct, ShopProduct,
    CustomerProfile, CustomerMachine, CustomerDocument, StaffDocument, 
    MachineMetric, MachineTelemetry, Distributor, StyleOverride
)


class StyleOverrideAdminForm(forms.ModelForm):
    """Colour pickers for override records."""

    class Meta:
        model = StyleOverride
        fields = "__all__"
        widgets = {
            "site_bg_color": forms.TextInput(attrs={"type": "color"}),
            "site_text_color": forms.TextInput(attrs={"type": "color"}),
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
            "link_color": forms.TextInput(attrs={"type": "color"}),
            "topbar_bg_color": forms.TextInput(attrs={"type": "color"}),
            "topbar_text_color": forms.TextInput(attrs={"type": "color"}),
            "header_bg_color": forms.TextInput(attrs={"type": "color"}),
            "header_text_color": forms.TextInput(attrs={"type": "color"}),
            "hero_bg_color": forms.TextInput(attrs={"type": "color"}),
            "hero_text_color": forms.TextInput(attrs={"type": "color"}),
            "hero_box_bg_color": forms.TextInput(attrs={"type": "color"}),
            "hero_box_bg_opacity": forms.NumberInput(attrs={"min": 0, "max": 100, "step": 1}),
            "section_alt_bg_color": forms.TextInput(attrs={"type": "color"}),
            "machines_section_bg_color": forms.TextInput(attrs={"type": "color"}),
            "machines_section_text_color": forms.TextInput(attrs={"type": "color"}),
            "distributors_section_bg_color": forms.TextInput(attrs={"type": "color"}),
            "distributors_section_text_color": forms.TextInput(attrs={"type": "color"}),
            "card_bg_color": forms.TextInput(attrs={"type": "color"}),
            "card_text_color": forms.TextInput(attrs={"type": "color"}),
            "footer_bg_color": forms.TextInput(attrs={"type": "color"}),
            "footer_text_color": forms.TextInput(attrs={"type": "color"}),
            "footer_link_color": forms.TextInput(attrs={"type": "color"}),
        }


@admin.register(StyleOverride)
class StyleOverrideAdmin(admin.ModelAdmin):
    form = StyleOverrideAdminForm
    list_display = ("name", "scope", "page_url_name", "section_key", "is_active", "sort_order")
    list_filter = ("scope", "is_active")
    search_fields = ("name", "page_url_name", "section_key")
    ordering = ("sort_order", "name")
    fieldsets = (
        ("Target", {
            "fields": ("name", "scope", "page_url_name", "section_key", "is_active", "sort_order"),
            "description": (
                "Page scope uses Django URL name (e.g. index, machines, tooling, shop, contact). "
                "Section scope matches data-section on the markup (e.g. hero, machines, distributors, footer)."
            )
        }),
        ("Colours", {
            "fields": (
                "site_bg_color", "site_text_color", "primary_color", "secondary_color", "link_color",
                "topbar_bg_color", "topbar_text_color",
                "header_bg_color", "header_text_color",
                "hero_bg_color", "hero_text_color", "hero_box_bg_color", "hero_box_bg_opacity",
                "section_alt_bg_color",
                "machines_section_bg_color", "machines_section_text_color",
                "distributors_section_bg_color", "distributors_section_text_color",
                "card_bg_color", "card_text_color",
                "footer_bg_color", "footer_text_color", "footer_link_color",
            )
        }),
        ("Advanced", {
            "fields": ("custom_css",),
            "classes": ("collapse",),
            "description": "Optional small CSS snippet for edge cases (applied after variables)."
        }),
    )

# --- 1. Define the Resource (How data is exported) ---
class SiteConfigResource(resources.ModelResource):
    class Meta:
        model = SiteConfiguration
        exclude = ('logo', 'favicon', 'site_bg_image') 

class SiteConfigurationAdminForm(forms.ModelForm):
    """Adds colour pickers for all color fields."""
    class Meta:
        model = SiteConfiguration
        fields = "__all__"
        widgets = {
            # -- Global --
            "site_bg_color": forms.TextInput(attrs={"type": "color"}),
            "site_text_color": forms.TextInput(attrs={"type": "color"}),
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
            "link_color": forms.TextInput(attrs={"type": "color"}),
            
            # -- Sections --
            "topbar_bg_color": forms.TextInput(attrs={"type": "color"}),
            "topbar_text_color": forms.TextInput(attrs={"type": "color"}),
            "hero_bg_color": forms.TextInput(attrs={"type": "color"}),
            "hero_text_color": forms.TextInput(attrs={"type": "color"}),
            "hero_box_bg_color": forms.TextInput(attrs={"type": "color"}),
            "hero_box_bg_opacity": forms.NumberInput(attrs={"min": 0, "max": 100, "step": 1}),
            "section_alt_bg_color": forms.TextInput(attrs={"type": "color"}),
            "machines_section_bg_color": forms.TextInput(attrs={"type": "color"}),
            "machines_section_text_color": forms.TextInput(attrs={"type": "color"}),
            "distributors_section_bg_color": forms.TextInput(attrs={"type": "color"}),
            "distributors_section_text_color": forms.TextInput(attrs={"type": "color"}),
            "card_bg_color": forms.TextInput(attrs={"type": "color"}),
            "card_text_color": forms.TextInput(attrs={"type": "color"}),

            # -- Header --
            "header_bg_color": forms.TextInput(attrs={"type": "color"}),
            "header_text_color": forms.TextInput(attrs={"type": "color"}),

            # -- Footer --
            "footer_bg_color": forms.TextInput(attrs={"type": "color"}),
            "footer_text_color": forms.TextInput(attrs={"type": "color"}),
            "footer_link_color": forms.TextInput(attrs={"type": "color"}),

            # -- Nav Buttons --
            "nav_btn_bg_color": forms.TextInput(attrs={"type": "color"}),
            "nav_btn_text_color": forms.TextInput(attrs={"type": "color"}),
            "nav_btn_border_color": forms.TextInput(attrs={"type": "color"}),
            "nav_btn_bg_hover_color": forms.TextInput(attrs={"type": "color"}),
            "nav_btn_text_hover_color": forms.TextInput(attrs={"type": "color"}),
            "nav_btn_border_hover_color": forms.TextInput(attrs={"type": "color"}),
            "nav_btn_bg_opacity": forms.NumberInput(attrs={"min": 0, "max": 100, "step": 1}),
            "nav_btn_border_opacity": forms.NumberInput(attrs={"min": 0, "max": 100, "step": 1}),
            "nav_btn_bg_hover_opacity": forms.NumberInput(attrs={"min": 0, "max": 100, "step": 1}),
            "nav_btn_border_hover_opacity": forms.NumberInput(attrs={"min": 0, "max": 100, "step": 1}),
        }

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(ImportExportModelAdmin):
    resource_class = SiteConfigResource
    form = SiteConfigurationAdminForm
    fieldsets = (
        ("Logo & Branding", {"fields": ("logo", "favicon")}),
        ("Global Theme (Body)", {
            "fields": (
                "site_bg_color", "site_bg_image", "site_text_color",
                "primary_color", "secondary_color", "link_color"
            ),
            "description": "General colors for the whole website."
        }),
        ("Layout Sections", {
            "fields": (
                "topbar_bg_color", "topbar_text_color",
                "hero_bg_color", "hero_text_color",
                "hero_box_bg_color", "hero_box_bg_opacity",
                "section_alt_bg_color",
                "card_bg_color", "card_text_color"
            ),
            "description": "Colors for specific strips and boxes."
        }),
        ("Header Styles", {
            "fields": ("header_bg_color", "header_text_color"),
            "classes": ("collapse",)
        }),
        ("Footer Styles", {
            "fields": ("footer_bg_color", "footer_text_color", "footer_link_color"),
            "classes": ("collapse",)
        }),
        ("Navigation Buttons", {
            "fields": (
            "nav_btn_bg_color","nav_btn_bg_opacity","nav_btn_text_color",
            "nav_btn_border_color","nav_btn_border_opacity",
            "nav_btn_bg_hover_color","nav_btn_bg_hover_opacity","nav_btn_text_hover_color",
            "nav_btn_border_hover_color","nav_btn_border_hover_opacity",
            "nav_btn_text_shadow",
            ),
            "classes": ("collapse",)
        }),
        ("Contact & Social", {
            "fields": (
                "phone_number", "email", "location",
                "linkedin_url", "facebook_url", "youtube_url"
            )
        }),
        ("Features (Homepage)", {"fields": ("feature_1", "feature_2", "feature_3")}),
    )
    def has_delete_permission(self, request, obj=None):
        return False

# --- New Form for Hero Slides (for the color picker) ---
class HeroSlideAdminForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = "__all__"
        widgets = {
            "bg_color": forms.TextInput(attrs={"type": "color"}),
        }

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    form = HeroSlideAdminForm  # Use the custom form
    list_display = ("title", "style", "sort_order", "is_active", "created_at")
    list_filter = ("style", "is_active")
    ordering = ("sort_order", "created_at")
    fieldsets = (
        ("Slide Type", {"fields": ("style", "is_active", "sort_order")}),
        ("Text Content", {"fields": ("title", "subtitle", "description")}),
        
        ("Foreground Media (The Machine)", {
            "fields": ("image", "video"),
            "description": "The floating image or video of the product."
        }),

        ("Full Screen Background", {
            "fields": ("bg_image", "bg_video", "bg_color", "bg_overlay_opacity"),
            "description": "The image, video, OR solid color that covers the entire slide."
        }),

        ("Content Box Styling", {
            "fields": ("card_background", "transparent_background"),
            "description": "Controls the appearance of the box containing the text."
        }),
        
        ("Call To Action", {"fields": ("cta_text", "cta_link")}),
        ("Settings", {"fields": ("show_features",)}),
    )

@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ("country_name", "flag_code", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    help_text = "Use lowercase country codes for flags (gb, us, ca, fr, de, etc)."

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

# --- User Admin Setup ---
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