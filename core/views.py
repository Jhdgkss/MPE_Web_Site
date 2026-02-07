import json
import logging
import math
import random
from collections import namedtuple
from decimal import Decimal

# import weasyprint  <-- REMOVED THIS LINE TO FIX THE CRASH

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .forms import SiteConfigurationForm
from .shop_forms import CheckoutForm
from .email_utils import send_order_emails

from .models import (
    BackgroundImage,
    CustomerDocument,
    CustomerMachine,
    CustomerProfile,
    StaffDocument,
    CustomerAddress,
    Distributor,
    CustomerContact,
    HeroSlide,
    MachineProduct,
    MachineTelemetry,
    ShopOrder,
    ShopOrderAddress,
    ShopOrderItem,
    ShopProduct,
    SiteConfiguration,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Helpers (safe: no DB access at import time)
# -----------------------------------------------------------------------------

def _background_images_json() -> str:
    imgs = BackgroundImage.objects.filter(is_active=True)
    urls = [img.image.url for img in imgs if getattr(img, "image", None)]
    return json.dumps(urls)


def _cart_get(request) -> dict:
    """
    Session cart format:
    {
      "<product_id>": {"qty": 2}
    }
    """
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    return cart


def _cart_save(request, cart: dict) -> None:
    request.session["cart"] = cart
    request.session.modified = True


def _cart_lines(cart: dict):
    """
    Returns (lines, totals)
    lines = [{"product": ShopProduct, "qty": int, "line_total": Decimal, "unit_price": Decimal}]
    totals = {"subtotal": Decimal, "count": int}
    """
    product_ids = []
    for k in cart.keys():
        try:
            product_ids.append(int(k))
        except Exception:
            continue

    products = {p.id: p for p in ShopProduct.objects.filter(id__in=product_ids, is_active=True)}
    lines = []
    subtotal = Decimal("0.00")
    count = 0

    for pid_str, item in cart.items():
        try:
            pid = int(pid_str)
        except Exception:
            continue
        p = products.get(pid)
        if not p:
            continue

        qty = int(item.get("qty", 0) or 0)
        if qty <= 0:
            continue

        unit_price = getattr(p, "price_gbp", None) or Decimal("0.00")
        try:
            unit_price = Decimal(str(unit_price))
        except Exception:
            unit_price = Decimal("0.00")

        line_total = unit_price * qty
        subtotal += line_total
        count += qty

        lines.append(
            {
                "product": p,
                "qty": qty,
                "unit_price": unit_price,
                "line_total": line_total,
            }
        )

    return lines, {"subtotal": subtotal, "count": count}


def _customer_ok(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return False
    try:
        prof = user.customer_profile
    except Exception:
        return False
    return bool(getattr(prof, "is_active", False))


# -----------------------------------------------------------------------------
# Public pages
# -----------------------------------------------------------------------------

def index(request):
    machines = MachineProduct.objects.filter(is_active=True)
    hero_slides = HeroSlide.objects.filter(is_active=True).order_by("sort_order", "created_at")
    distributors = Distributor.objects.filter(is_active=True).order_by("sort_order")

    ctx = {
        "machines": machines,
        "featured_machines": machines[:3],
        "hero_slides": hero_slides,
        "distributors": distributors,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/index.html", ctx)


def contact(request):
    ctx = {"background_images_json": _background_images_json()}
    return render(request, "core/contact.html", ctx)


def documents(request):
    ctx = {"background_images_json": _background_images_json()}
    return render(request, "core/documents.html", ctx)


def search(request):
    q = (request.GET.get("q") or "").strip()

    machines = MachineProduct.objects.filter(is_active=True)
    shop_items = ShopProduct.objects.filter(is_active=True)

    if q:
        machines = machines.filter(Q(name__icontains=q) | Q(description__icontains=q))
        shop_items = shop_items.filter(Q(name__icontains=q) | Q(description__icontains=q))

    ctx = {
        "q": q,
        "machines": machines[:12],
        "shop_items": shop_items[:12],
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/search.html", ctx)


# -----------------------------------------------------------------------------
# Shop pages (Phase 1 + 2)
# -----------------------------------------------------------------------------

def shop(request):
    """
    Main shop page uses AJAX to load products.
    """
    query = request.GET.get('q')
    products = ShopProduct.objects.filter(is_active=True).order_by("sort_order", "name")

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )

    ctx = {
        "products": products,
        "search_query": query,
        "background_images_json": _background_images_json()
    }
    return render(request, "core/shop.html", ctx)


@require_GET
def api_products(request):
    """
    AJAX product feed for the shop grid.
    """
    products = ShopProduct.objects.filter(is_active=True).order_by("sort_order", "name")

    # Optional global toggle (hide prices)
    show_prices_global = True
    try:
        cfg = SiteConfiguration.get_config()
        show_prices_global = bool(getattr(cfg, "shop_show_prices", True))
    except Exception:
        # If config table not ready, default True
        show_prices_global = True

    data = []
    for p in products:
        price_val = None
        if show_prices_global and bool(getattr(p, "show_price", True)):
            try:
                price_val = float(p.price_gbp)
            except Exception:
                price_val = None

        slug = getattr(p, "slug", "") or ""
        data.append(
            {
                "id": p.id,
                "name": p.name,
                "sku": getattr(p, "sku", "") or "",
                "category": getattr(p, "category", "") or "",
                "description": p.description,
                "price": price_val,
                "image_url": p.image.url if p.image else "",
                "stock_status": "In Stock" if getattr(p, "in_stock", True) else "Out of Stock",
                "slug": slug,
                "detail_url": reverse("shop_product_detail", kwargs={"slug": slug}) if slug else "",
                "created_at": p.created_at.isoformat() if getattr(p, "created_at", None) else "",
            }
        )
    return JsonResponse(data, safe=False)


def shop_product_detail(request, slug):
    """
    SEO friendly product detail page.
    """
    product = get_object_or_404(ShopProduct, slug=slug, is_active=True)
    ctx = {
        "product": product,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/shop_product_detail.html", ctx)


def cart_view(request):
    cart = _cart_get(request)
    lines, totals = _cart_lines(cart)
    
    # Map helper output to template expectations
    cart_items = []
    for line in lines:
        cart_items.append({
            'product': line['product'],
            'quantity': line['qty'],
            'line_total': line['line_total'],
        })

    ctx = {
        "cart_items": cart_items,
        "subtotal": totals["subtotal"],
        "total": totals["subtotal"],
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/cart.html", ctx)


@csrf_exempt
def api_cart_add(request):
    """
    POST JSON: { "product_id": 123, "qty": 1 }
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        payload = {}

    pid = payload.get("product_id")
    qty = int(payload.get("qty") or 1)

    try:
        pid = int(pid)
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid product_id"}, status=400)

    product = ShopProduct.objects.filter(id=pid, is_active=True).first()
    if not product:
        return JsonResponse({"ok": False, "error": "Product not found"}, status=404)

    cart = _cart_get(request)
    key = str(pid)
    current = int(cart.get(key, {}).get("qty", 0) or 0)
    cart[key] = {"qty": max(1, current + max(1, qty))}
    _cart_save(request, cart)

    _, totals = _cart_lines(cart)
    return JsonResponse({"ok": True, "cart_count": totals["count"]})


@csrf_exempt
def api_cart_update(request):
    """
    POST JSON: { "items": [{"product_id": 123, "qty": 2}, ...] }
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        payload = {}

    items = payload.get("items") or []
    cart = _cart_get(request)

    for it in items:
        try:
            pid = int(it.get("product_id"))
            qty = int(it.get("qty") or 0)
        except Exception:
            continue

        key = str(pid)
        if qty <= 0:
            cart.pop(key, None)
        else:
            cart[key] = {"qty": qty}

    _cart_save(request, cart)
    lines, totals = _cart_lines(cart)

    return JsonResponse(
        {
            "ok": True,
            "cart_count": totals["count"],
            "subtotal": str(totals["subtotal"]),
        }
    )


def cart_remove(request, product_id: int):
    cart = _cart_get(request)
    cart.pop(str(product_id), None)
    _cart_save(request, cart)
    return redirect("cart")


def update_cart(request, product_id):
    """
    Handles updating quantities or removing items from the cart via POST form.
    """
    if request.method == 'POST':
        cart = _cart_get(request)
        str_id = str(product_id)
        
        action = request.POST.get('action')
        
        if action == 'remove':
            if str_id in cart:
                del cart[str_id]
                messages.success(request, "Item removed from basket.")
                
        elif action == 'update':
            try:
                quantity = int(request.POST.get('quantity', 1))
                if quantity > 0:
                    cart[str_id] = {"qty": quantity}
                    messages.success(request, "Basket updated.")
                else:
                    if str_id in cart:
                        del cart[str_id]
            except ValueError:
                pass

        _cart_save(request, cart)
        
    return redirect('cart')


def _autofill_checkout_initial(request):
    """
    Phase 2: if user authenticated, use CustomerProfile + latest address if any.
    """
    initial = {}

    if not request.user.is_authenticated:
        return initial

    # Try CustomerProfile
    try:
        prof = request.user.customer_profile
        initial.update(
            {
                "name": getattr(prof, "contact_name", "") or request.user.get_username(),
                "company": getattr(prof, "company_name", "") or "",
                "email": getattr(prof, "email", "") or getattr(request.user, "email", "") or "",
                "phone": getattr(prof, "phone", "") or "",
            }
        )
    except Exception:
        initial.update(
            {
                "name": request.user.get_username(),
                "email": getattr(request.user, "email", "") or "",
            }
        )

    # Pull most recent address from CustomerAddress (if it exists)
    try:
        addr = CustomerAddress.objects.filter(user=request.user).order_by("-created_at").first()
        if addr:
            initial.update(
                {
                    "address_1": addr.address_1,
                    "address_2": addr.address_2,
                    "city": addr.city,
                    "county": addr.county,
                    "postcode": addr.postcode,
                    "country": addr.country,
                }
            )
    except Exception:
        pass

    return initial


def checkout(request):
    cart = _cart_get(request)
    lines, totals = _cart_lines(cart)
    if not lines:
        messages.info(request, "Your basket is empty.")
        return redirect("shop")

    if request.method == "POST":
        form = CheckoutForm(request.POST, user=request.user if request.user.is_authenticated else None)
        if form.is_valid():
            cleaned = form.cleaned_data

            # 1. Handle Contact (Create or Get)
            contact, _ = CustomerContact.objects.get_or_create(
                email=cleaned["email"],
                defaults={
                    "name": cleaned["name"],
                    "company": cleaned.get("company", ""),
                    "phone": cleaned.get("phone", ""),
                    "user": request.user if request.user.is_authenticated else None,
                }
            )

            # 2. Create the order
            order = ShopOrder.objects.create(
                user=request.user if request.user.is_authenticated else None,
                contact=contact,
                order_number=cleaned.get("order_number") or "",
                notes=cleaned.get("notes") or "",
                status="NEW",
            )

            # 3. Save address snapshot
            ShopOrderAddress.objects.create(
                order=order,
                label=cleaned.get("address_label") or "Delivery",
                address_1=cleaned["address_1"],
                address_2=cleaned.get("address_2") or "",
                city=cleaned["city"],
                county=cleaned.get("county") or "",
                postcode=cleaned["postcode"],
                country=cleaned.get("country") or "UK",
            )

            # 4. Save items
            for line in lines:
                p = line["product"]
                ShopOrderItem.objects.create(
                    order=order,
                    product=p,
                    sku=getattr(p, "sku", "") or "",
                    product_name=p.name,
                    quantity=line["qty"],
                    unit_price_gbp=line["unit_price"],
                )

            # Optional: store customer address book entry
            if request.user.is_authenticated:
                try:
                    # Check if we need to create a contact record for the user first if it doesn't exist
                    if not hasattr(request.user, 'customer_contacts'):
                        pass # Logic handled by get_or_create above usually

                    CustomerAddress.objects.create(
                        contact=contact,
                        address_1=cleaned["address_1"],
                        address_2=cleaned.get("address_2") or "",
                        city=cleaned["city"],
                        county=cleaned.get("county") or "",
                        postcode=cleaned["postcode"],
                        country=cleaned.get("country") or "UK",
                        label=cleaned.get("address_label") or "Default",
                    )
                except Exception:
                    pass

            # Email staff + customer
            try:
                cfg = SiteConfiguration.get_config()
                sales_email = getattr(cfg, "email", "")
            except Exception:
                sales_email = ""

            subject_staff = f"New Shop Order #{order.id} - {contact.company or contact.name}"
            subject_customer = f"Order received #{order.id}"

            staff_html = render_to_string("emails/order_notification_staff.html", {"order": order})
            cust_html = render_to_string("core/emails/order_customer.html", {"order": order})

            # Send emails (customer + internal) using EmailConfiguration (admin-configurable)
            try:
                send_order_emails(order, request=request)
            except Exception as e:
                logger.error(f"Failed to send order emails for order {order.id}: {e}")

            # Clear cart
            _cart_save(request, {})
            return redirect("order_success", order_id=order.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CheckoutForm(initial=_autofill_checkout_initial(request), user=request.user if request.user.is_authenticated else None)

    ctx = {
        "form": form,
        "lines": lines,
        "totals": totals,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/checkout.html", ctx)


def order_success(request, order_id: int):
    order = get_object_or_404(ShopOrder, id=order_id)
    ctx = {"order": order, "background_images_json": _background_images_json()}
    return render(request, "core/order_success.html", ctx)


def order_pdf(request, order_id: int):
    import weasyprint  # Safe local import
    order = get_object_or_404(ShopOrder, id=order_id)
    
    # Get site config for Logo/Header and calculate total
    config = SiteConfiguration.get_config()
    items = order.items.all()
    total = sum(item.line_total() for item in items)

    ctx = {"order": order, "config": config, "total": total}

    html_string = render_to_string("core/order_pdf.html", ctx, request=request)
    pdf_file = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    filename = f"Order_{order.order_number or order.id}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# -----------------------------------------------------------------------------
# Staff area
# -----------------------------------------------------------------------------

def staff_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("staff_dashboard")

    next_url = request.GET.get("next") or reverse("staff_dashboard")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Login failed. Please check your username and password.")
        elif not user.is_staff:
            messages.error(request, "This account does not have access to the staff area.")
        else:
            login(request, user)
            return redirect(request.POST.get("next") or next_url)

    ctx = {"next": next_url, "background_images_json": _background_images_json()}
    return render(request, "core/staff_login.html", ctx)


def staff_logout(request):
    logout(request)
    return redirect("index")


def staff_dashboard(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect(f"{reverse('staff_login')}?next={reverse('staff_dashboard')}")

    # Determine Staff Level
    # Default to Level 1 (Docs & Forms) for basic staff
    level = 1
    if request.user.is_superuser:
        level = 3
    elif hasattr(request.user, "staff_profile"):
        level = request.user.staff_profile.level

    orders = []
    if level >= 2:
        orders = ShopOrder.objects.all().order_by("-created_at")[:20]

    docs = StaffDocument.objects.filter(is_active=True).order_by("-uploaded_at")

    ctx = {"orders": orders, "docs": docs, "level": level, "background_images_json": _background_images_json()}
    return render(request, "core/staff_dashboard.html", ctx)


def staff_order_list(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect(f"{reverse('staff_login')}?next={reverse('staff_order_list')}")

    # Permission check (Level 2+)
    level = 1
    if request.user.is_superuser:
        level = 3
    elif hasattr(request.user, "staff_profile"):
        level = request.user.staff_profile.level
    
    if level < 2:
        messages.error(request, "You do not have permission to view orders.")
        return redirect("staff_dashboard")

    orders = ShopOrder.objects.all().order_by("-created_at")
    ctx = {"orders": orders, "background_images_json": _background_images_json()}
    return render(request, "core/staff_order_list.html", ctx)


def staff_order_detail(request, order_id):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect(f"{reverse('staff_login')}?next={reverse('staff_order_detail', args=[order_id])}")

    # Permission check (Level 2+)
    level = 1
    if request.user.is_superuser:
        level = 3
    elif hasattr(request.user, "staff_profile"):
        level = request.user.staff_profile.level
    
    if level < 2:
        messages.error(request, "You do not have permission to view orders.")
        return redirect("staff_dashboard")

    order = get_object_or_404(ShopOrder, id=order_id)
    ctx = {"order": order, "background_images_json": _background_images_json()}
    return render(request, "core/staff_order_detail.html", ctx)


def staff_order_status(request, order_id, new_status):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect(f"{reverse('staff_login')}?next={reverse('staff_order_detail', args=[order_id])}")

    # Permission check (Level 2+)
    level = 1
    if request.user.is_superuser:
        level = 3
    elif hasattr(request.user, "staff_profile"):
        level = request.user.staff_profile.level
    
    if level < 2:
        messages.error(request, "You do not have permission to update orders.")
        return redirect("staff_dashboard")

    order = get_object_or_404(ShopOrder, id=order_id)
    if new_status in dict(ShopOrder.STATUS_CHOICES):
        order.status = new_status
        order.save()
        messages.success(request, f"Order status updated to {order.get_status_display()}.")
    
    return redirect("staff_order_detail", order_id=order.id)


def staff_homepage_editor(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect(f"{reverse('staff_login')}?next={reverse('staff_homepage_editor')}")

    config = SiteConfiguration.get_config()

    if request.method == "POST":
        form = SiteConfigurationForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Saved.")
            return redirect("staff_homepage_editor")
        messages.error(request, "Please fix the highlighted fields.")
    else:
        form = SiteConfigurationForm(instance=config)

    ctx = {"form": form, "config": config, "background_images_json": _background_images_json()}
    return render(request, "core/staff_homepage_editor.html", ctx)


# -----------------------------------------------------------------------------
# Customer portal
# -----------------------------------------------------------------------------

_Machine = namedtuple("PortalMachine", "id name serial_number")
_Metric = namedtuple("PortalMetric", "metric_key value unit ts sparkline")


def _sparkline(values, width=120, height=34, pad=3):
    if not values:
        return ""
    mn = min(values)
    mx = max(values)
    if mx == mn:
        mx = mn + 1.0
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = pad + (width - 2 * pad) * (i / max(1, n - 1))
        y = pad + (height - 2 * pad) * (1 - ((v - mn) / (mx - mn)))
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def _build_sample_portal_data(username: str):
    seed = sum(ord(c) for c in (username or "user")) % 10_000
    random.seed(seed)

    machines = [
        _Machine(1, "MPE i6 Tray Sealer", "I6-" + str(1000 + seed % 900)),
        _Machine(2, "MPE i3 Tray Sealer", "I3-" + str(2000 + seed % 900)),
    ]

    now = timezone.now()
    latest_by_machine = {}
    for m in machines:
        t = [i for i in range(24)]
        base_ppm = random.uniform(18, 32)
        ppm_series = [base_ppm + 3 * (random.random() - 0.5) + 2 * math.sin(i / 3) for i in t]

        latest_by_machine[m.id] = [
            _Metric("Packs/min", f"{ppm_series[-1]:.1f}", "ppm", now, _sparkline(ppm_series)),
            _Metric("Status", "RUNNING", "", now, ""),
        ]
    return machines, latest_by_machine


def portal_login(request):
    if _customer_ok(request.user):
        return redirect("portal_home")

    next_url = request.GET.get("next") or reverse("portal_home")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Login failed. Please check your username and password.")
        elif user.is_staff:
            messages.error(request, "This is a staff account. Please use the Staff login.")
        else:
            try:
                prof = user.customer_profile
            except Exception:
                prof = None
            if not prof:
                messages.error(request, "This account is not enabled for the customer portal.")
            elif not prof.is_active:
                messages.error(request, "This customer portal account is disabled.")
            else:
                login(request, user)
                return redirect(request.POST.get("next") or next_url)

    ctx = {"next": next_url, "background_images_json": _background_images_json()}
    return render(request, "core/portal_login.html", ctx)


def portal_logout(request):
    logout(request)
    return redirect("index")


def portal_home(request):
    if not _customer_ok(request.user):
        return redirect(f"{reverse('portal_login')}?next={reverse('portal_home')}")
    machines, _latest = _build_sample_portal_data(request.user.get_username())
    ctx = {"machines": machines, "docs": [], "background_images_json": _background_images_json()}
    return render(request, "core/portal_home.html", ctx)


def portal_documents(request):
    if not _customer_ok(request.user):
        return redirect(f"{reverse('portal_login')}?next={reverse('portal_documents')}")
    docs = CustomerDocument.objects.filter(customer=request.user, is_active=True).order_by("-uploaded_at")
    ctx = {"docs": docs, "background_images_json": _background_images_json()}
    return render(request, "core/portal_documents.html", ctx)


def portal_dashboard(request):
    if not _customer_ok(request.user):
        return redirect(f"{reverse('portal_login')}?next={reverse('portal_dashboard')}")
    machines, latest_by_machine = _build_sample_portal_data(request.user.get_username())

    headline = {"machines_online": len(machines), "alerts": 0}
    ctx = {
        "machines": machines,
        "latest_metrics_by_machine": latest_by_machine,
        "headline": headline,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/portal_dashboard.html", ctx)


def portal_orders(request):
    """
    Phase 2: order history for logged-in customers.
    """
    if not _customer_ok(request.user):
        return redirect(f"{reverse('portal_login')}?next={reverse('portal_orders')}")

    orders = (
        ShopOrder.objects.filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related("items")
    )

    ctx = {"orders": orders, "background_images_json": _background_images_json()}
    return render(request, "core/portal_orders.html", ctx)


# -----------------------------------------------------------------------------
# API: Machine Metrics Ingest & Read
# -----------------------------------------------------------------------------

@csrf_exempt
def telemetry_ingest(request):
    """
    Receives JSON POST from machine_client.py and saves to DB.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            MachineTelemetry.objects.create(
                machine_id=data.get("machine_id"),
                ppm=data.get("ppm"),
                temp=data.get("temp"),
                batch_count=data.get("batch_count"),
                status=data.get("status"),
            )
            return JsonResponse({"status": "success", "message": "Telemetry saved"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)


@require_GET
def machine_metrics_api(request):
    if not _customer_ok(request.user):
        return JsonResponse({"error": "Unauthorized"}, status=403)

    machine_id = request.GET.get("machine_id", "i6")

    machines_db = {
        "i6": {"name": "MPE i6 Tray Sealer"},
        "i3": {"name": "MPE i3 Tray Sealer"},
        "test": {"name": "LAB-01 Test Unit"},
    }
    config = machines_db.get(machine_id, {"name": "Unknown Machine"})

    latest = MachineTelemetry.objects.filter(machine_id=machine_id).first()

    if latest:
        return JsonResponse(
            {
                "machine_id": machine_id,
                "name": config["name"],
                "status": latest.status,
                "metrics": {
                    "ppm": latest.ppm,
                    "temp": latest.temp,
                    "batch": latest.batch_count,
                    "utilisation": 88 if latest.status == "RUNNING" else 0,
                },
            }
        )

    return JsonResponse(
        {
            "machine_id": machine_id,
            "name": config["name"],
            "status": "OFFLINE",
            "metrics": {"ppm": 0, "temp": 0, "batch": 0, "utilisation": 0},
        }
    )


@csrf_exempt
def api_import_stock(request):
    """
    Receives JSON list of products and updates the database.
    Requires Basic Authentication (Username/Password of a Staff member).
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)

        username = data.get("username")
        password = data.get("password")
        products_data = data.get("products", [])

        user = authenticate(username=username, password=password)
        if not user or not user.is_staff:
            return JsonResponse({"status": "error", "message": "Invalid credentials or not staff"}, status=403)

        created_count = 0
        updated_count = 0

        for item in products_data:
            obj, created = ShopProduct.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item.get("description", ""),
                    "price_gbp": item.get("price", 0.0),
                    "stock_status": "In Stock",
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return JsonResponse({"status": "success", "created": created_count, "updated": updated_count})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
