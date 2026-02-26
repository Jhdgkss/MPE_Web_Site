from django.contrib import admin
from django import forms
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


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


# ---------- User admin (show username + email, require email on creation) ----------
try:
    User = get_user_model()

    class CustomUserCreationForm(UserCreationForm):
        """Require email when creating users in admin."""

        class Meta(UserCreationForm.Meta):
            model = User
            fields = ("username", "email")

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if "email" in self.fields:
                self.fields["email"].required = True

    class CustomUserAdmin(DjangoUserAdmin):
        add_form = CustomUserCreationForm
        form = UserChangeForm
        model = User

        list_display = ("username", "email", "is_staff", "is_active", "date_joined")
        search_fields = ("username", "email", "first_name", "last_name")
        ordering = ("username",)

        # Ensure email is visible/editable in the change form
        fieldsets = (
            (None, {"fields": ("username", "password")}),
            ("Personal info", {"fields": ("first_name", "last_name", "email")}),
            (
                "Permissions",
                {
                    "fields": (
                        "is_active",
                        "is_staff",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    )
                },
            ),
            ("Important dates", {"fields": ("last_login", "date_joined")}),
        )

        add_fieldsets = (
            (
                None,
                {
                    "classes": ("wide",),
                    "fields": ("username", "email", "password1", "password2", "is_staff", "is_active"),
                },
            ),
        )

    # Replace default User admin with our version
    try:
        admin.site.unregister(User)
    except admin.sites.NotRegistered:
        pass
    admin.site.register(User, CustomUserAdmin)

except Exception:
    # Never break admin if auth model differs
    pass
