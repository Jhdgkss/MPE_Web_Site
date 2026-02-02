from django.urls import path
from . import views

urlpatterns = [
    # Public
    path("", views.index, name="index"),
    path("machines/", views.machines, name="machines"),
    path("tooling/", views.tooling, name="tooling"),
    path("contact/", views.contact, name="contact"),

    # Shop
    path("shop/", views.shop, name="shop"),
    path("api/products/", views.api_products, name="api_products"),
    path("shop/product/<slug:slug>/", views.shop_product_detail, name="shop_product_detail"),

    # Cart / Checkout
    path("shop/cart/", views.cart_view, name="cart_view"),
    path("shop/cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("shop/cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("shop/checkout/", views.checkout, name="checkout"),

    # Customer portal
    path("documents/", views.documents, name="documents"),
    path("customer/orders/", views.portal_orders, name="portal_orders"),
    path("customer/login/", views.portal_login, name="portal_login"),
    path("customer/logout/", views.portal_logout, name="portal_logout"),

    # Staff
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
]
