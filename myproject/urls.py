from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.templatetags.static import static as static_file

urlpatterns = [
    path("admin/", admin.site.urls),

    # Fix for favicon requests (Google / browsers look for /favicon.ico)
    path("favicon.ico", RedirectView.as_view(url=static_file("assets/favicon.png"))),

    # Main site routes
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)