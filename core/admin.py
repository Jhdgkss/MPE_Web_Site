from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db import connection
from import_export import resources 
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html

from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import json

from .models import (
    SiteConfiguration, EmailConfiguration, PDFConfiguration, BackgroundImage, HeroSlide,
    MachineProduct, MachineProductImage, MachineProductDocument, MachineProductVideo, MachineProductStat, MachineProductFeature,
    ShopProduct,
    CustomerProfile, StaffProfile, CustomerMachine, CustomerDocument, StaffDocument,
    CustomerContact, CustomerAddress, ShopOrder, ShopOrderItem, ShopOrderAddress,
    MachineMetric, MachineTelemetry, Distributor
)


class MachineProductJSONImportForm(forms.Form):
    json_file = forms.FileField(
        help_text="Upload a Machine Product JSON file exported/generated for this site."
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
        ("Shop", {
    "fields": ("shop_show_prices",),
    "description": "If disabled, prices are hidden and customers request a quote.",
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

class MachineProductImageInline(admin.TabularInline):
    model = MachineProductImage
    extra = 0


class MachineProductDocumentInline(admin.TabularInline):
    model = MachineProductDocument
    extra = 0


class MachineProductVideoInline(admin.TabularInline):
    model = MachineProductVideo
    extra = 0



class MachineProductStatInline(admin.TabularInline):
    model = MachineProductStat
    extra = 0


class MachineProductFeatureInline(admin.TabularInline):
    model = MachineProductFeature
    extra = 0


@admin.register(MachineProduct)
class MachineProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "tagline", "description")
    prepopulated_fields = {"slug": ("name",)}
# Use HTML color picker for the image frame background colour
def formfield_for_dbfield(self, db_field, request, **kwargs):
    from django import forms
    if db_field.name == "image_frame_bg_color":
        kwargs["widget"] = forms.TextInput(attrs={"type": "color"})
    return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        (
            "Card / Listing",
            {
                "fields": (
                    "name",
                    "slug",
                    "tagline",
                    "description",
                    "image",
                    "sort_order",
                    "is_active",
                )
            },
        ),
        (
            "Machine Page",
            {
                "fields": (
                    "hero_image",
                    "image_frame_bg_color",
                    "hero_title",
                    "hero_subtitle",
                    "overview_title",
                    "overview_body",
                    "key_features",
                )
            },
        ),
        (
            "Primary Links",
            {"fields": ("spec_pdf", "external_link")},
        ),
    )
    inlines = [
        MachineProductImageInline,
        MachineProductDocumentInline,
        MachineProductVideoInline,
        MachineProductStatInline,
        MachineProductFeatureInline,
    ]


# Use a custom change list template so we can show an "Import from JSON" button.
change_list_template = "admin/core/machineproduct/change_list.html"

def get_urls(self):
    urls = super().get_urls()
    custom = [
        path(
            "import-json/",
            self.admin_site.admin_view(self.import_json_view),
            name="core_machineproduct_import_json",
        ),
    ]
    # Put our URLs BEFORE the built-ins so "import-json" isn't treated as an object_id.
    return custom + urls

def import_json_view(self, request):
    if request.method == "POST":
        form = MachineProductJSONImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                payload = json.load(form.cleaned_data["json_file"])
            except Exception as e:
                messages.error(request, f"Could not read JSON file: {e}")
                return render(request, "admin/core/machineproduct/import_json.html", {"form": form})

            machine_data = payload.get("machine") or {}
            slug = machine_data.get("slug") or ""
            if not slug:
                messages.error(request, "JSON is missing machine.slug")
                return render(request, "admin/core/machineproduct/import_json.html", {"form": form})

            obj, created = MachineProduct.objects.get_or_create(slug=slug)

            # Update machine fields (only those that exist on the model)
            for key, value in machine_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            obj.save()

            replace_related = payload.get("replace_related", True)
            if replace_related:
                MachineProductStat.objects.filter(machine=obj).delete()
                MachineProductFeature.objects.filter(machine=obj).delete()
                MachineProductDocument.objects.filter(machine=obj).delete()

            # Stats
            for s in payload.get("stats", []) or []:
                s = dict(s)
                MachineProductStat.objects.create(
                    machine=obj,
                    label=s.get("label", ""),
                    value=s.get("value", ""),
                    unit=s.get("unit", "") or "",
                    sort_order=int(s.get("sort_order", 0) or 0),
                    is_highlight=bool(s.get("is_highlight", False)),
                )

            # Features (icon must match choices)
            valid_icons = {c[0] for c in MachineProductFeature.ICON_CHOICES}
            for f in payload.get("features", []) or []:
                f = dict(f)
                icon = f.get("icon") or MachineProductFeature.ICON_CUSTOM
                if icon not in valid_icons:
                    icon = MachineProductFeature.ICON_CUSTOM
                MachineProductFeature.objects.create(
                    machine=obj,
                    icon=icon,
                    title=f.get("title", "")[:60],
                    short_text=f.get("short_text", "")[:120],
                    sort_order=int(f.get("sort_order", 0) or 0),
                    is_highlight=bool(f.get("is_highlight", False)),
                )

            # Documents (URL links are Railway-safe; file upload via admin if needed)
            for d in payload.get("documents", []) or []:
                d = dict(d)
                MachineProductDocument.objects.create(
                    machine=obj,
                    title=d.get("title", "")[:140],
                    url=d.get("url", "") or "",
                    sort_order=int(d.get("sort_order", 0) or 0),
                )

            messages.success(
                request,
                f"Imported machine product '{obj.name}' ({'created' if created else 'updated'}).",
            )
            return redirect("../")

    else:
        form = MachineProductJSONImportForm()

    return render(request, "admin/core/machineproduct/import_json.html", {"form": form})

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


# -------------------------------------------------------------------------
# MachineProduct JSON Import (robust + Railway-safe)
# This block *overrides* the currently-registered MachineProduct admin to add
# an /import-json/ admin view. It intentionally maps legacy keys:
#   hero_heading -> hero_title
#   hero_subheading -> hero_subtitle
# -------------------------------------------------------------------------
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import json as _json

class MachineProductJSONImportForm(forms.Form):
    json_file = forms.FileField()

def _coerce_machine_payload(payload: dict) -> dict:
    if isinstance(payload, dict) and "machine" in payload and isinstance(payload["machine"], dict):
        return payload["machine"]
    return payload if isinstance(payload, dict) else {}

def _map_legacy_keys(machine_data: dict) -> dict:
    md = dict(machine_data or {})
    # legacy -> current field names
    if "hero_heading" in md and "hero_title" not in md:
        md["hero_title"] = md.pop("hero_heading")
    if "hero_subheading" in md and "hero_subtitle" not in md:
        md["hero_subtitle"] = md.pop("hero_subheading")
    return md

def _install_machineproduct_json_import():
    try:
        from django.contrib import admin
        from .models import MachineProduct
    except Exception:
        return

    existing = admin.site._registry.get(MachineProduct)
    if not existing:
        return

    BaseAdmin = existing.__class__

    # avoid double-install
    if getattr(BaseAdmin, "_json_import_installed", False):
        return

    class MachineProductAdminWithJSONImport(BaseAdmin):
        change_list_template = "admin/core/machineproduct/change_list.html"

        def get_urls(self):
            urls = super().get_urls()
            custom = [
                path(
                    "import-json/",
                    self.admin_site.admin_view(self.import_json_view),
                    name="core_machineproduct_import_json",
                ),
            ]
            # IMPORTANT: put our URLs BEFORE the built-ins so "import-json" isn't treated as an object_id.
            return custom + urls

        def import_json_view(self, request):
            if request.method == "POST":
                form = MachineProductJSONImportForm(request.POST, request.FILES)
                if form.is_valid():
                    try:
                        payload = _json.load(form.cleaned_data["json_file"])
                    except Exception as e:
                        messages.error(request, f"Could not read JSON file: {e}")
                        return render(request, "admin/core/machineproduct/import_json.html", {"form": form})

                    machine_data = _map_legacy_keys(_coerce_machine_payload(payload))
                    replace_related = True
                    if isinstance(payload, dict):
                        replace_related = bool(payload.get("replace_related", True))

                    slug = (machine_data.get("slug") or "").strip()
                    name = (machine_data.get("name") or "").strip()

                    if not slug and name:
                        # let model save() auto-generate slug if blank; but our importer prefers explicit slug
                        slug = ""

                    # Create/update object.
                    # IMPORTANT: don't pass unknown fields in defaults (will raise FieldError).
                    defaults = {}
                    if name:
                        defaults["name"] = name

                    # Use current model field names.
                    if "hero_title" in machine_data:
                        defaults["hero_title"] = machine_data.get("hero_title") or ""
                    if "hero_subtitle" in machine_data:
                        defaults["hero_subtitle"] = machine_data.get("hero_subtitle") or ""

                    if slug:
                        obj, _created = MachineProduct.objects.get_or_create(slug=slug, defaults=defaults)
                    else:
                        # fall back to name lookup (best-effort)
                        obj, _created = MachineProduct.objects.get_or_create(name=name or "Machine", defaults=defaults)

                    # Apply remaining scalar fields
                    for k, v in machine_data.items():
                        if k in ("slug",):
                            continue
                        # Skip file fields in JSON (upload via admin)
                        if k in ("hero_image", "image", "spec_pdf"):
                            continue
                        if hasattr(obj, k):
                            try:
                                setattr(obj, k, v)
                            except Exception:
                                pass

                    # Ensure required basics
                    if not getattr(obj, "name", None):
                        obj.name = name or (slug.replace("-", " ").upper() if slug else "Machine")
                    obj.save()

                    # Related rows (optional)
                    try:
                        from .models import MachineProductStat, MachineProductFeature, MachineProductDocument
                    except Exception:
                        MachineProductStat = MachineProductFeature = MachineProductDocument = None

                    if replace_related:
                        if MachineProductStat:
                            MachineProductStat.objects.filter(machine=obj).delete()
                        if MachineProductFeature:
                            MachineProductFeature.objects.filter(machine=obj).delete()
                        if MachineProductDocument:
                            MachineProductDocument.objects.filter(machine=obj).delete()

                    if MachineProductStat and isinstance(payload, dict):
                        for s in payload.get("stats", []) or []:
                            if isinstance(s, dict):
                                MachineProductStat.objects.create(machine=obj, **s)

                    if MachineProductFeature and isinstance(payload, dict):
                        for f in payload.get("features", []) or []:
                            if isinstance(f, dict):
                                MachineProductFeature.objects.create(machine=obj, **f)

                    if MachineProductDocument and isinstance(payload, dict):
                        for d in payload.get("documents", []) or []:
                            if isinstance(d, dict):
                                # Support either "url" or "file" keys; we only set attrs that exist.
                                doc = MachineProductDocument(machine=obj)
                                for k, v in d.items():
                                    if hasattr(doc, k):
                                        setattr(doc, k, v)
                                doc.save()

                    messages.success(request, "Machine product imported successfully.")
                    return redirect("../")
            else:
                form = MachineProductJSONImportForm()

            return render(request, "admin/core/machineproduct/import_json.html", {"form": form})

    # Replace registration with subclass that includes import support.
    try:
        admin.site.unregister(MachineProduct)
    except Exception:
        pass
    admin.site.register(MachineProduct, MachineProductAdminWithJSONImport)

    # mark installed on BaseAdmin to prevent re-install loops
    MachineProductAdminWithJSONImport._json_import_installed = True
    BaseAdmin._json_import_installed = True

try:
    _install_machineproduct_json_import()
except Exception:
    # Never break admin startup because of importer
    pass
