from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db import connection
from import_export import resources 
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html

from .models import (
    SiteConfiguration, EmailConfiguration, PDFConfiguration, BackgroundImage, HeroSlide, MachineProduct, ShopProduct,
    CustomerProfile, StaffProfile, CustomerMachine, CustomerDocument, StaffDocument,
    CustomerContact, CustomerAddress, ShopOrder, ShopOrderItem, ShopOrderAddress,
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

            # -- Page Specific --
            "contact_hero_bg_color": forms.TextInput(attrs={"type": "color"}),
            "contact_hero_text_color": forms.TextInput(attrs={"type": "color"}),
            "contact_section_bg_color": forms.TextInput(attrs={"type": "color"}),
            "contact_section_text_color": forms.TextInput(attrs={"type": "color"}),
            
            "shop_hero_bg_color": forms.TextInput(attrs={"type": "color"}),
            "shop_hero_text_color": forms.TextInput(attrs={"type": "color"}),
            "shop_section_bg_color": forms.TextInput(attrs={"type": "color"}),
            "shop_section_text_color": forms.TextInput(attrs={"type": "color"}),

            "documents_hero_bg_color": forms.TextInput(attrs={"type": "color"}),
            "documents_hero_text_color": forms.TextInput(attrs={"type": "color"}),
            "documents_section_bg_color": forms.TextInput(attrs={"type": "color"}),
            "documents_section_text_color": forms.TextInput(attrs={"type": "color"}),

            "tooling_hero_bg_color": forms.TextInput(attrs={"type": "color"}),
            "tooling_hero_text_color": forms.TextInput(attrs={"type": "color"}),
            "tooling_section_bg_color": forms.TextInput(attrs={"type": "color"}),
            "tooling_section_text_color": forms.TextInput(attrs={"type": "color"}),
            "tooling_section_heading_color": forms.TextInput(attrs={"type": "color"}),
            "tooling_feature_bg_color": forms.TextInput(attrs={"type": "color"}),
            "tooling_feature_text_color": forms.TextInput(attrs={"type": "color"}),

            "portal_hero_bg_color": forms.TextInput(attrs={"type": "color"}),
            "portal_hero_text_color": forms.TextInput(attrs={"type": "color"}),
            "portal_section_bg_color": forms.TextInput(attrs={"type": "color"}),
            "portal_section_text_color": forms.TextInput(attrs={"type": "color"}),
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
        ("Page: Contact", {
            "fields": ("contact_hero_bg_color", "contact_hero_text_color", "contact_section_bg_color", "contact_section_text_color"),
            "classes": ("collapse",)
        }),
        ("Page: Shop", {
            "fields": ("shop_hero_bg_color", "shop_hero_text_color", "shop_section_bg_color", "shop_section_text_color"),
            "classes": ("collapse",)
        }),
        ("Page: Documents", {
            "fields": ("documents_hero_bg_color", "documents_hero_text_color", "documents_section_bg_color", "documents_section_text_color"),
            "classes": ("collapse",)
        }),
        ("Page: Tooling", {
            "fields": ("tooling_hero_bg_color", "tooling_hero_text_color", "tooling_section_bg_color", "tooling_section_text_color", "tooling_section_heading_color", "tooling_feature_bg_color", "tooling_feature_text_color"),
            "classes": ("collapse",)
        }),
        ("Page: Customer Portal", {
            "fields": ("portal_hero_bg_color", "portal_hero_text_color", "portal_section_bg_color", "portal_section_text_color"),
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

class HeroSlideAdminForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = "__all__"
        widgets = {
            "bg_color": forms.TextInput(attrs={"type": "color"}),
        }

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    form = HeroSlideAdminForm
    list_display = ("title", "style", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("style", "is_active")

class DistributorAdminForm(forms.ModelForm):
    class Meta:
        model = Distributor
        fields = "__all__"
        widgets = {
            "bg_color": forms.TextInput(attrs={"type": "color"}),
            "text_color": forms.TextInput(attrs={"type": "color"}),
            "border_color": forms.TextInput(attrs={"type": "color"}),
            "description_color": forms.TextInput(attrs={"type": "color"}),
            "btn_bg_color": forms.TextInput(attrs={"type": "color"}),
            "btn_text_color": forms.TextInput(attrs={"type": "color"}),
        }

@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    form = DistributorAdminForm
    list_display = ("country_name", "logo_preview", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 30px; max-width: 50px;" />', obj.logo.url)
        if obj.flag_code:
            return format_html('<span class="fi fi-{}" style="font-size: 20px;"></span>', obj.flag_code)
        return "-"
    logo_preview.short_description = "Logo/Flag"

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

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "level")
    list_editable = ("level",)

admin.site.register(CustomerMachine)
admin.site.register(CustomerDocument)
admin.site.register(StaffDocument)
admin.site.register(MachineMetric)
admin.site.register(MachineTelemetry)

@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "email", "phone", "user", "updated_at")
    list_filter = ("company",)
    search_fields = ("name", "company", "email", "phone")


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ("contact", "label", "postcode", "is_default")
    list_filter = ("is_default", "country")
    search_fields = ("contact__name", "contact__company", "postcode", "city", "address_1")


class ShopOrderItemInline(admin.TabularInline):
    model = ShopOrderItem
    extra = 0
    readonly_fields = ("product_name", "sku", "unit_price_gbp", "quantity")


@admin.register(ShopOrder)
class ShopOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "status",
        "order_number",
        "contact",
        "user",
        "email_sent_to_customer",
        "email_sent_to_internal",
        "email_sent_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "contact__name", "contact__company", "contact__email")
    inlines = [ShopOrderItemInline]

    readonly_fields = (
        "email_sent_to_customer",
        "email_sent_to_internal",
        "email_sent_at",
        "email_last_error",
    )


@admin.register(ShopOrderAddress)
class ShopOrderAddressAdmin(admin.ModelAdmin):
    list_display = ("order", "label", "postcode", "city")
    search_fields = ("order__id", "postcode", "city", "address_1")


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    """Singleton editor for transactional email settings."""

    fieldsets = (
        ("Sender", {"fields": ("from_email", "reply_to_email")}),
        ("Recipients", {"fields": ("internal_recipients", "send_to_customer", "send_to_internal")}),
        ("PDF Attachment", {"fields": ("attach_order_pdf", "pdf_filename_template")}),
        ("Subject Templates", {"fields": ("customer_subject_template", "internal_subject_template")}),
        ("Footer", {"fields": ("footer_note",)}),
    )

    def has_add_permission(self, request):
        # Singleton
        return not EmailConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PDFConfiguration)
class PDFConfigurationAdmin(admin.ModelAdmin):
    """Singleton editor for PDF branding/settings."""

    fieldsets = (
        (
            "Branding",
            {
                "fields": (
                    "pdf_logo",
                    "company_name",
                    "header_email",
                    "header_phone",
                    "header_location",
                )
            },
        ),
        (
            "Layout",
            {
                "fields": (
                    "document_title",
                    "accent_color",
                    "footer_text",
                    "show_page_numbers",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        # Singleton
        return not PDFConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
