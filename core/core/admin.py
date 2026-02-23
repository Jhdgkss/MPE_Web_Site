
# PATCHED SECTION — fix indentation inside MachineProductAdmin

from django.contrib import admin

class MachineProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

    # Use HTML color picker for the image frame background colour
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        from django import forms
        if db_field.name == "image_frame_bg_color":
            kwargs["widget"] = forms.TextInput(attrs={"type": "color"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        # keep your existing fieldsets content below this line
    )
