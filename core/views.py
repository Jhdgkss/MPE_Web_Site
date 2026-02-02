import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_GET

from .models import (
    HeroSlide,
    MachineProduct,
    ShopProduct,
    SiteConfiguration,
    CustomerProfile,
    MachineTelemetry,
    Distributor,
    CustomerDocument,
    CustomerMachine,
    CustomerContact,
    CustomerAddress,
    ShopOrder,
    ShopOrderItem,
    ShopOrderAddress,
)

from .shop_forms import CheckoutForm


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_site_config():
    try:
        return SiteConfiguration.get_config()
    except Exception:
        return SiteConfiguration.objects.first()


def _background_images_json():
    try:
        from .models import BackgroundImage
        imgs = BackgroundImage.objects.filter(is_active=True)
        return json.dumps([img.image.url for img in imgs if img.image])
    except Exception:
        return "[]"


def _cart_get(request):
    return request.session.get("cart", {})


def _cart_save(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def _cart_count(cart):
    return sum(int(v.get("qty", 0)) for v in cart.values())


def _cart_total(cart):
    return sum(float(v.get("price", 0)) * int(v.get("qty", 0)) for v in cart.values())


def _is_customer_user(user):
    return user.is_authenticated and not user.is_staff and not user.is_superuser


def _prefill_checkout_initial(request):
    initial = {}
    user = request.user
    if not _is_customer_user(user):
        return initial

    if user.email:
        initial["email"] = user.email
    name = f"{user.first_name} {user.last_name}".strip()
    if name:
        initial["name"] = name

    profile = CustomerProfile.objects.filter(user=user).first()
    if profile and profile.company_name:
        initial["company"] = profile.company_name

    last_order = ShopOrder.objects.filter(user=user).order_by("-created_at").first()
    if last_order:
        c = last_order.contact
        if c:
            initial.setdefault("name", c.name)
            initial.setdefault("company", c.company)
            initial.setdefault("phone", c.phone)
            initial.setdefault("email", c.email)

        addr = last_order.order_addresses.first()
        if addr:
            initial.update({
                "address_1": addr.address_1,
                "address_2": addr.address_2,
                "city": addr.city,
                "county": addr.county,
                "postcode": addr.postcode,
                "country": addr.country,
            })

    return initial


# -----------------------------------------------------------------------------
# Public pages
# -----------------------------------------------------------------------------
def index(request):
    cfg = get_site_config()
    return render(
        request,
        "core/index.html",
        {
            "site_config": cfg,
            "hero_slides": HeroSlide.objects.filter(is_active=True),
            "machines": MachineProduct.objects.filter(is_active=True),
            "distributors": Distributor.objects.filter(is_active=True),
            "background_images_json": _background_images_json(),
        },
    )


def machines(request):
    return render(
        request,
        "core/machines.html",
        {
            "site_config": get_site_config(),
            "machines": MachineProduct.objects.filter(is_active=True),
        },
    )


def tooling(request):
    return render(request, "core/tooling.html", {"site_config": get_site_config()})


def contact(request):
    return render(request, "core/contact.html", {"site_config": get_site_config()})


# -----------------------------------------------------------------------------
# Shop
# -----------------------------------------------------------------------------
def shop(request):
    return render(request, "core/shop.html", {"site_config": get_site_config()})


@require_GET
def api_products(request):
    cfg = get_site_config()
    data = []
    for p in ShopProduct.objects.filter(is_active=True):
        data.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "price_gbp": float(p.price_gbp or 0),
            "show_price": p.show_price and cfg.shop_show_prices,
            "image": p.image.url if p.image else "",
            "url": reverse("shop_product_detail", kwargs={"slug": p.slug}),
        })
    return JsonResponse(data, safe=False)


def shop_product_detail(request, slug):
    product = get_object_or_404(ShopProduct, slug=slug, is_active=True)
    cfg = get_site_config()
    return render(
        request,
        "core/shop_product_detail.html",
        {
            "site_config": cfg,
            "product": product,
            "show_price": product.show_price and cfg.shop_show_prices,
        },
    )


# -----------------------------------------------------------------------------
# Cart / Checkout
# -----------------------------------------------------------------------------
def cart_view(request):
    cart = _cart_get(request)
    return render(
        request,
        "core/cart.html",
        {
            "site_config": get_site_config(),
            "cart_items": cart,
            "cart_total": _cart_total(cart),
        },
    )


def cart_add(request, product_id):
    product = get_object_or_404(ShopProduct, id=product_id)
    cart = _cart_get(request)
    pid = str(product.id)
    cart.setdefault(pid, {"name": product.name, "qty": 0, "price": float(product.price_gbp or 0)})
    cart[pid]["qty"] += 1
    _cart_save(request, cart)
    return redirect("cart_view")


def cart_remove(request, product_id):
    cart = _cart_get(request)
    cart.pop(str(product_id), None)
    _cart_save(request, cart)
    return redirect("cart_view")


def checkout(request):
    cart = _cart_get(request)
    if not cart:
        messages.info(request, "Your basket is empty.")
        return redirect("shop")

    initial = _prefill_checkout_initial(request)
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            contact = CustomerContact.objects.create(
                user=request.user if _is_customer_user(request.user) else None,
                name=cd["name"],
                company=cd.get("company", ""),
                phone=cd.get("phone", ""),
                email=cd["email"],
            )

            order = ShopOrder.objects.create(
                user=request.user if _is_customer_user(request.user) else None,
                contact=contact,
                order_number=cd.get("order_number", ""),
            )

            for pid, item in cart.items():
                product = ShopProduct.objects.filter(id=int(pid)).first()
                ShopOrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=item["name"],
                    unit_price_gbp=item["price"],
                    quantity=item["qty"],
                )

            _cart_save(request, {})
            return render(request, "core/order_success.html", {"order": order})

    else:
        form = CheckoutForm(initial=initial)

    return render(
        request,
        "core/checkout.html",
        {
            "site_config": get_site_config(),
            "form": form,
            "cart_total": _cart_total(cart),
        },
    )


# -----------------------------------------------------------------------------
# Customer Portal
# -----------------------------------------------------------------------------
def documents(request):
    if not _is_customer_user(request.user):
        return redirect("portal_login")

    docs = CustomerDocument.objects.filter(customer=request.user)
    return render(
        request,
        "core/portal_documents.html",
        {
            "site_config": get_site_config(),
            "documents": docs,
        },
    )


def portal_orders(request):
    if not _is_customer_user(request.user):
        return redirect("portal_login")

    return render(
        request,
        "core/portal_orders.html",
        {
            "site_config": get_site_config(),
            "orders": ShopOrder.objects.filter(user=request.user),
        },
    )


def portal_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            return redirect("portal_orders")
        messages.error(request, "Login failed")
    return render(request, "core/customer_login.html", {"site_config": get_site_config()})


def portal_logout(request):
    logout(request)
    return redirect("index")


# -----------------------------------------------------------------------------
# Staff
# -----------------------------------------------------------------------------
def staff_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user and user.is_staff:
            login(request, user)
            return redirect("staff_dashboard")
        messages.error(request, "Login failed")
    return render(request, "core/staff_login.html", {"site_config": get_site_config()})


def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect("staff_login")
    return render(request, "core/staff_home.html", {"site_config": get_site_config()})
