from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # Main navigation
    path("machines/", views.index, name="machines"),  # anchor handled in template (same page)
    path("tooling/", views.tooling, name="tooling"),
    path("shop/", views.shop, name="shop"),

    path("contact/", views.contact, name="contact"),
    path("documents/", views.documents, name="documents"),
    path("search/", views.search, name="search"),
    path("api/products/", views.api_products, name="api_products"),

    # Customer Portal
    path("portal/login/", views.portal_login, name="portal_login"),
    path("portal/logout/", views.portal_logout, name="portal_logout"),
    path("portal/", views.portal_home, name="portal_home"),
    path("portal/documents/", views.portal_documents, name="portal_documents"),
    path("portal/dashboard/", views.portal_dashboard, name="portal_dashboard"),

    # Staff area (separate from /admin)
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/logout/", views.staff_logout, name="staff_logout"),
    path("staff/", views.staff_home, name="staff_home"),
]
