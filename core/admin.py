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
    MachineMetric, MachineTelemetry, Distributor
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
                "machines_section_bg_color", "machines_section_text_color",
                "distributors_section_bg_color", "distributors_section_text_color",
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
            ),
            "description": "Contact info and social media links."
        }),
        ("Features", {
            "fields": ("feature_1", "feature_2", "feature_3"),
            "description": "Three key features shown on the homepage."
        }),
        ("Advanced", {
            "fields": ("custom_css",),
            "classes": ("collapse",),
            "description": "Global custom CSS."
        }),
    )

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "style", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("style", "is_active")

@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ("country_name", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")

@admin.register(MachineProduct)
class MachineProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")

@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price_gbp", "in_stock", "is_active")
    list_filter = ("category", "in_stock", "is_active")

admin.site.register(BackgroundImage)
admin.site.register(CustomerProfile)
admin.site.register(CustomerMachine)
admin.site.register(CustomerDocument)
admin.site.register(StaffDocument)
admin.site.register(MachineMetric)
admin.site.register(MachineTelemetry)