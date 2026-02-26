from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .password_reset_views import CustomerPasswordResetRequestView

# Optional tooling page import wrapper
try:
    from .tooling import tooling as tooling_view
except ImportError:
    tooling_view = None

urlpatterns = [
    # --- 1. Main Pages ---
    path("", views.index, name="index"),
    path("machines/", views.machines_list, name="machines_list"),
    path("machines/<slug:slug>/", views.machine_detail, name="machine_detail"),
    path("contact/", views.contact, name="contact"),
    path("contact/submit/", views.contact_submit, name="contact_submit"),
    path("diag/email/", views.diag_email, name="diag_email"),
    path("documents/", views.documents, name="documents"),
    path("search/", views.search, name="search"),

    # --- Legal / SEO ---
    path("cookie-policy/", views.cookie_policy, name="cookie_policy"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),

    # --- 2. Shop & Checkout ---
    path("shop/", views.shop, name="shop"),
    path("shop/product/<slug:slug>/", views.shop_product_detail, name="shop_product_detail"),

    path("shop/cart/", views.cart_view, name="cart"),
    path("shop/cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("shop/checkout/", views.checkout, name="checkout"),
    path("shop/order-success/<int:order_id>/", views.order_success, name="order_success"),
    path("shop/order-pdf/<int:order_id>/", views.order_pdf, name="order_pdf"),

    # Shop APIs (Ajax)
    path("shop/cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("api/cart/add/", views.api_cart_add, name="api_cart_add"),
    path("api/cart/update/", views.api_cart_update, name="api_cart_update"),
    path("api/products/", views.api_products, name="api_products"),

    # --- 3. Optional Tooling Section ---
    path("tooling/", tooling_view if tooling_view else views.shop, name="tooling"),

    # --- 4. Customer Portal ---
    path("customer/login/", views.portal_login, name="portal_login"),
    path("customer/logout/", views.portal_logout, name="portal_logout"),
    path("customer/", views.portal_home, name="portal_home"),
    path("customer/documents/", views.portal_documents, name="portal_documents"),
    path("customer/dashboard/", views.portal_dashboard, name="portal_dashboard"),
    path("customer/orders/", views.portal_orders, name="portal_orders"),

    # Password reset (customer portal) - sends via Brevo
    path(
        "customer/password-reset/",
        CustomerPasswordResetRequestView.as_view(),
        name="customer_password_reset",
    ),
    path(
        "customer/password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="customer_password_reset_done",
    ),
    path(
        "customer/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url="/customer/reset/done/",
        ),
        name="customer_password_reset_confirm",
    ),
    path(
        "customer/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="customer_password_reset_complete",
    ),

    # --- 5. Staff Area ---
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/logout/", views.staff_logout, name="staff_logout"),
    path("staff/homepage-editor/", views.staff_homepage_editor, name="staff_homepage_editor"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/orders/", views.staff_order_list, name="staff_order_list"),
    path("staff/orders/<int:order_id>/", views.staff_order_detail, name="staff_order_detail"),
    path("staff/orders/<int:order_id>/status/<str:new_status>/", views.staff_order_status, name="staff_order_status"),

    # --- 6. Machine Data APIs ---
    path("api/machine-metrics/", views.machine_metrics_api, name="api_machine_metrics"),
    path("api/ingest/", views.telemetry_ingest, name="api_ingest"),
    path("api/import-stock/", views.api_import_stock, name="api_import_stock"),

    # --- 7. Diagnostics ---
    # The view 'email_diagnostic' is not defined in core/views.py. Commenting out to prevent server crash.
    # path("diag/email/", views.email_diagnostic, name="email_diagnostic"),
]
