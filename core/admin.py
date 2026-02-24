from django.contrib import admin
from django import forms
from django.db import models

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
