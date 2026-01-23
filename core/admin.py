from django.contrib import admin
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigAdmin(admin.ModelAdmin):
    # This prevents adding new items if one already exists.
    # We only want ONE configuration row for the whole site.
    def has_add_permission(self, request):
        if SiteConfiguration.objects.exists():
            return False
        return True