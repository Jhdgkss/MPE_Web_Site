from django.urls import path
from . import views

# Optional tooling page (kept separate so core/views.py can stay untouched).
try:
    from .tooling import tooling as tooling_view  # type: ignore
except Exception:
    tooling_view = None

urlpatterns = [
    path("", views.index, name="index"),
    path("shop/", views.shop, name="shop"),
    path("contact/", views.contact, name="contact"),
    path("documents/", views.documents, name="documents"),
    path("search/", views.search, name="search"),
    path("api/products/", views.api_products, name="api_products"),

    # Tooling (future: spec generator form)
    # If you later create views.tooling in core/views.py, you can swap this line to that.
    path("tooling/", tooling_view if tooling_view else views.shop, name="tooling"),

    # Staff area (separate from /admin)
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/logout/", views.staff_logout, name="staff_logout"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
]
