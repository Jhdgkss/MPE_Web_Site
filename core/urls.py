from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("shop/", views.shop, name="shop"),
    path("contact/", views.contact, name="contact"),
    path("documents/", views.documents, name="documents"),
    path("search/", views.search, name="search"),
    path("api/products/", views.api_products, name="api_products"),

    # Staff area (separate from /admin)
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/logout/", views.staff_logout, name="staff_logout"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
]
