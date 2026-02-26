from django.contrib import admin
from django import forms
from django.db import models

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
        # Ensure email appears on add/edit pages
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
        if (
            isinstance(db_field, models.CharField)
            and db_field.name.endswith("_color")
        ):
            kwargs["widget"] = ColorInput()
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# ---------- Auto-register all core models safely ----------
try:
    from . import models as core_models

    for model in core_models.__dict__.values():
        if isinstance(model, type) and issubclass(model, models.Model):
            try:
                admin.site.register(model, BaseColorAdmin)
            except admin.sites.AlreadyRegistered:
                pass
except Exception:
    # Fail safe — never crash admin import
    pass
