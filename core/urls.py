from django.urls import path
from . import views

# Optional tooling page
try:
    from .tooling import tooling as tooling_view
except Exception:
    tooling_view = None

urlpatterns = [
    path("", views.index, name="index"),
    path("shop/", views.shop, name="shop"),
    path("contact/", views.contact, name="contact"),
    path("documents/", views.documents, name="documents"),
    path("search/", views.search, name="search"),
    path("api/products/", views.api_products, name="api_products"),

    path("tooling/", tooling_view if tooling_view else views.shop, name="tooling"),

    # Customer portal
    path("customer/login/", views.portal_login, name="portal_login"),
    path("customer/logout/", views.portal_logout, name="portal_logout"),
    path("customer/", views.portal_home, name="portal_home"),
    path("customer/documents/", views.portal_documents, name="portal_documents"),
    path("customer/dashboard/", views.portal_dashboard, name="portal_dashboard"),
    
    # --- API ENDPOINTS ---
    path("api/machine-metrics/", views.machine_metrics_api, name="api_machine_metrics"), # Dashboard reads this
    path("api/ingest/", views.telemetry_ingest, name="api_ingest"), # Machine sends to this
    # ---------------------

    # Staff area
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/logout/", views.staff_logout, name="staff_logout"),
    path("staff/homepage-editor/", views.staff_homepage_editor, name="staff_homepage_editor"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),

    #Remote Desktop API Importer
    path("api/import-stock/", views.api_import_stock, name="api_import_stock"),

]