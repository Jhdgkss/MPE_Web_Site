import json

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.shortcuts import redirect, render
from django.urls import path

# --- Optional: improve built-in User admin (email required + searchable) ---
try:
    from django.contrib.auth.models import User
    from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
    from django.contrib.auth.forms import UserCreationForm

    class UserCreateWithEmailForm(UserCreationForm):
        email = forms.EmailField(required=True)

        def clean_email(self):
            email = (self.cleaned_data.get("email") or "").strip()
            if not email:
                raise forms.ValidationError("Email is required.")
            return email

    class UserAdmin(DjangoUserAdmin):
        add_form = UserCreateWithEmailForm
        list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
        search_fields = ("username", "email", "first_name", "last_name")
        ordering = ("username",)
        fieldsets = (
            (None, {"fields": ("username", "password")}),
            ("Personal info", {"fields": ("first_name", "last_name", "email")}),
            ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
            ("Important dates", {"fields": ("last_login", "date_joined")}),
        )
        add_fieldsets = (
            (None, {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            }),
        )

    try:
        admin.site.unregister(User)
    except admin.sites.NotRegistered:
        pass
    admin.site.register(User, UserAdmin)
except Exception:
    # Never crash admin import
    pass


# ---------- Safe Colour Picker Widget ----------
class ColorInput(forms.TextInput):
    input_type = "color"


class BaseColorAdmin(admin.ModelAdmin):
    """
    Safe base admin that:
    - Adds HTML5 colour picker to any CharField ending with '_color'
    - Does NOT assume any model fields exist
    - Avoids Django system check errors
    """
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.CharField) and db_field.name.endswith("_color"):
            kwargs["widget"] = ColorInput()
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# ---------- Import models ----------
from . import models as core_models
from .models import (
    MachineProduct,
    MachineProductDocument,
    MachineProductFeature,
    MachineProductImage,
    MachineProductStat,
    MachineProductVideo,
)


# ---------- Custom MachineProduct admin with JSON import ----------
@admin.register(MachineProduct)
class MachineProductAdmin(BaseColorAdmin):
    list_display = ("name", "slug", "is_active", "sort_order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "tagline", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")
    change_list_template = "admin/core/machineproduct/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-json/",
                self.admin_site.admin_view(self.import_json_view),
                name="core_machineproduct_import_json",
            ),
        ]
        return custom_urls + urls

    def import_json_view(self, request):
        if request.method == "POST":
            json_file = request.FILES.get("json_file")
            if not json_file:
                messages.error(request, "Please choose a JSON file to upload.")
                return redirect(request.path)

            try:
                data = json.load(json_file)
            except Exception as exc:
                messages.error(request, f"Could not read JSON file: {exc}")
                return redirect(request.path)

            try:
                name = (data.get("name") or "").strip()
                slug = (data.get("slug") or "").strip()

                if not name:
                    messages.error(request, "JSON import failed: 'name' is required.")
                    return redirect(request.path)

                defaults = {
                    "name": name,
                    "tagline": data.get("tagline", ""),
                    "description": data.get("description", ""),
                    "hero_title": data.get("hero_title", ""),
                    "hero_subtitle": data.get("hero_subtitle", ""),
                    "overview_title": data.get("overview_title", "Overview"),
                    "overview_body": data.get("overview_body", ""),
                    "external_link": data.get("external_link", ""),
                    "sort_order": data.get("sort_order", 0),
                    "is_active": data.get("is_active", True),
                    "key_features": self._normalise_key_features(data.get("key_features", "")),
                    "image_frame_bg_color": data.get("image_frame_bg_color") or "#ffffff",
                }

                if slug:
                    product, created = MachineProduct.objects.update_or_create(
                        slug=slug,
                        defaults=defaults,
                    )
                else:
                    product, created = MachineProduct.objects.update_or_create(
                        name=name,
                        defaults=defaults,
                    )

                self._replace_stats(product, data.get("stats", []))
                self._replace_features(product, data.get("features", []))
                self._replace_documents(product, data.get("documents", []))
                self._replace_videos(product, data.get("videos", []))
                self._replace_gallery(product, data.get("gallery_images", []))

                msg = (
                    f"Machine product '{product.name}' imported successfully."
                    if created
                    else f"Machine product '{product.name}' updated successfully."
                )
                messages.success(request, msg)
                return redirect("../")

            except Exception as exc:
                messages.error(request, f"JSON import failed: {exc}")
                return redirect(request.path)

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Import machine product from JSON",
        }
        return render(request, "admin/core/machineproduct/import_json.html", context)

    def _normalise_key_features(self, value):
        if isinstance(value, list):
            return "\n".join(str(v).strip() for v in value if str(v).strip())
        if isinstance(value, str):
            return value
        return ""

    def _replace_stats(self, product, stats):
        MachineProductStat.objects.filter(machine=product).delete()
        if not isinstance(stats, list):
            return

        for i, stat in enumerate(stats):
            if not isinstance(stat, dict):
                continue
            value = str(stat.get("value", "")).strip()
            label = str(stat.get("label", "")).strip()
            unit = str(stat.get("unit", "")).strip()
            if not value and not label:
                continue
            MachineProductStat.objects.create(
                machine=product,
                value=value,
                label=label,
                unit=unit,
                sort_order=stat.get("sort_order", i),
                is_highlight=bool(stat.get("is_highlight", False)),
            )

    def _replace_features(self, product, features):
        MachineProductFeature.objects.filter(machine=product).delete()
        if not isinstance(features, list):
            return

        icon_map = {
            "speed": MachineProductFeature.ICON_SPEED,
            "gauge": MachineProductFeature.ICON_SPEED,
            "tooling": MachineProductFeature.ICON_TOOLING,
            "wrench": MachineProductFeature.ICON_TOOLING,
            "electric": MachineProductFeature.ICON_ELECTRIC,
            "bolt": MachineProductFeature.ICON_ELECTRIC,
            "build": MachineProductFeature.ICON_BUILD,
            "industry": MachineProductFeature.ICON_BUILD,
            "hygiene": MachineProductFeature.ICON_HYGIENE,
            "shield": MachineProductFeature.ICON_HYGIENE,
            "support": MachineProductFeature.ICON_SUPPORT,
            "headset": MachineProductFeature.ICON_SUPPORT,
            "map": MachineProductFeature.ICON_MAP,
            "wind": MachineProductFeature.ICON_MAP,
            "custom": MachineProductFeature.ICON_CUSTOM,
            "star": MachineProductFeature.ICON_CUSTOM,
            "wifi": MachineProductFeature.ICON_CUSTOM,
        }

        for i, feature in enumerate(features):
            if not isinstance(feature, dict):
                continue

            raw_icon = str(feature.get("icon", feature.get("icon_key", "speed"))).strip().lower()
            icon = icon_map.get(raw_icon, MachineProductFeature.ICON_CUSTOM)
            title = str(feature.get("title", "")).strip()
            short_text = str(
                feature.get("short_text", feature.get("description", ""))
            ).strip()

            if not title and not short_text:
                continue

            MachineProductFeature.objects.create(
                machine=product,
                icon=icon,
                title=title or "Feature",
                short_text=short_text,
                sort_order=feature.get("sort_order", i),
                is_highlight=bool(feature.get("is_highlight", False)),
            )

    def _replace_documents(self, product, documents):
        MachineProductDocument.objects.filter(machine=product).delete()
        if not isinstance(documents, list):
            return

        for i, doc in enumerate(documents):
            if not isinstance(doc, dict):
                continue
            title = str(doc.get("title", "")).strip()
            url = str(doc.get("url", "")).strip()
            if not title and not url:
                continue
            MachineProductDocument.objects.create(
                machine=product,
                title=title or f"Document {i + 1}",
                url=url,
                sort_order=doc.get("sort_order", i),
            )

    def _replace_videos(self, product, videos):
        MachineProductVideo.objects.filter(machine=product).delete()
        if not isinstance(videos, list):
            return

        for i, vid in enumerate(videos):
            if not isinstance(vid, dict):
                continue
            title = str(vid.get("title", "")).strip()
            video_url = str(vid.get("video_url", vid.get("url", ""))).strip()
            embed_url = str(vid.get("embed_url", "")).strip()
            if not video_url and not embed_url:
                continue
            MachineProductVideo.objects.create(
                machine=product,
                title=title,
                video_url=video_url,
                embed_url=embed_url,
                sort_order=vid.get("sort_order", i),
            )

    def _replace_gallery(self, product, images):
        """
        Supports JSON references for captions only.
        File upload import is not handled here because JSON cannot upload
        image binaries directly through Django admin.
        """
        if not isinstance(images, list):
            return

        # Clear existing placeholder gallery rows only if JSON explicitly includes gallery_images
        MachineProductImage.objects.filter(machine=product).delete()

        for i, item in enumerate(images):
            if not isinstance(item, dict):
                continue
            caption = str(item.get("caption", "")).strip()
            # We cannot assign an actual image file from plain JSON here.
            # Skip rows that do not have a real uploaded file.
            if caption:
                MachineProductImage.objects.create(
                    machine=product,
                    caption=caption,
                    sort_order=item.get("sort_order", i),
                )


# ---------- Auto-register all remaining core models safely ----------
EXCLUDED_MODELS = {
    MachineProduct,
}

for model in core_models.__dict__.values():
    if isinstance(model, type) and issubclass(model, models.Model):
        if model in EXCLUDED_MODELS:
            continue
        try:
            admin.site.register(model, BaseColorAdmin)
        except admin.sites.AlreadyRegistered:
            pass
        except Exception:
            pass