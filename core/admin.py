
# --- JSON Import Support (safe add-on) ---
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
import json

class MachineProductJSONImportForm(forms.Form):
    json_file = forms.FileField()


def _patch_machineproduct_admin():
    from django.contrib import admin
    from .models import MachineProduct, MachineProductStat, MachineProductFeature, MachineProductDocument

    # Find the already-registered admin
    ma = admin.site._registry.get(MachineProduct)
    if not ma:
        return

    # Only patch once
    if hasattr(ma.__class__, "_json_import_patched"):
        return

    original_get_urls = ma.get_urls

    def import_json_view(self, request):
        if request.method == "POST":
            form = MachineProductJSONImportForm(request.POST, request.FILES)
            if form.is_valid():
                data = json.load(form.cleaned_data["json_file"])
                machine_data = data.get("machine", {})
                slug = machine_data.get("slug")

                obj, _ = MachineProduct.objects.get_or_create(slug=slug)

                for k, v in machine_data.items():
                    if hasattr(obj, k):
                        setattr(obj, k, v)
                obj.save()

                if data.get("replace_related", True):
                    MachineProductStat.objects.filter(machine=obj).delete()
                    MachineProductFeature.objects.filter(machine=obj).delete()
                    MachineProductDocument.objects.filter(machine=obj).delete()

                for s in data.get("stats", []):
                    MachineProductStat.objects.create(machine=obj, **s)

                for f in data.get("features", []):
                    MachineProductFeature.objects.create(machine=obj, **f)

                for d in data.get("documents", []):
                    MachineProductDocument.objects.create(machine=obj, **d)

                messages.success(request, "JSON import successful.")
                return redirect("../")

        else:
            form = MachineProductJSONImportForm()

        return render(request, "admin/core/machineproduct/import_json.html", {"form": form})

    def get_urls(self):
        urls = original_get_urls()
        custom = [
            path("import-json/", self.admin_site.admin_view(import_json_view.__get__(self)), name="core_machineproduct_import_json"),
        ]
        return custom + urls

    ma.__class__.get_urls = get_urls
    ma.__class__._json_import_patched = True


# Run patch at import time
try:
    _patch_machineproduct_admin()
except Exception:
    pass
