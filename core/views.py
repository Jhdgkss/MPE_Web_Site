import json
import random
from collections import namedtuple
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json



# UPDATED IMPORTS: Added CustomerDocument and CustomerMachine
from .models import (
    BackgroundImage,
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
from .forms import SiteConfigurationForm
from .shop_forms import CheckoutForm


def _background_images_json() -> str:
    imgs = BackgroundImage.objects.filter(is_active=True)
    urls = [img.image.url for img in imgs if img.image]
    return json.dumps(urls)


def index(request):
    machines = MachineProduct.objects.filter(is_active=True)
    hero_slides = HeroSlide.objects.filter(is_active=True).order_by("sort_order", "created_at")
    
    # Fetch active distributors
    distributors = Distributor.objects.filter(is_active=True).order_by("sort_order")

    ctx = {
        "machines": machines,
        "featured_machines": machines[:3],
        "hero_slides": hero_slides,
        "distributors": distributors,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/index.html", ctx)


def shop(request):
    ctx = {"background_images_json": _background_images_json()}
    return render(request, "core/shop.html", ctx)


@require_GET
def api_products(request):
    products = ShopProduct.objects.filter(is_active=True).order_by("sort_order", "name")
    data = []
    for p in products:
        data.append(
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "category": p.category,
                "description": p.description,
                "price": float(p.price_gbp) if getattr(p, "show_price", True) else None,
                "image_url": p.image.url if p.image else "",
                "stock_status": "In Stock" if p.in_stock else "Out of Stock",
                "slug": p.slug,
                "detail_url": reverse("shop_product_detail", kwargs={"slug": p.slug}),
                "created_at": p.created_at.isoformat(),
            }
        )
    return JsonResponse(data, safe=False)


def shop_product_detail(request, slug):
    """Product detail page (SEO-friendly)."""
    product = get_object_or_404(ShopProduct, slug=slug, is_active=True)
    return render(request, "core/shop_product_detail.html", {"product": product})


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
        machines = machines.filter(name__icontains=q) | machines.filter(description__icontains=q)
        shop_items = shop_items.filter(name__icontains=q) | shop_items.filter(description__icontains=q)

    ctx = {
        "q": q,
        "machines": machines[:12],
        "shop_items": shop_items[:12],
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/search.html", ctx)


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
    ctx = {"background_images_json": _background_images_json()}
    return render(request, "core/staff_dashboard.html", ctx)


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
    rng = __import__("random")
    rng.seed(seed)

    machines = [
        _Machine(1, "MPE i6 Tray Sealer", "I6-" + str(1000 + seed % 900)),
        _Machine(2, "MPE i3 Tray Sealer", "I3-" + str(2000 + seed % 900)),
    ]

    now = timezone.now()
    latest_by_machine = {}
    for m in machines:
        t = [i for i in range(24)]
        base_ppm = rng.uniform(18, 32)
        ppm_series = [base_ppm + 3 * (rng.random() - 0.5) + 2 * __import__("math").sin(i / 3) for i in t]
        
        latest_by_machine[m.id] = [
            _Metric("Packs/min", f"{ppm_series[-1]:.1f}", "ppm", now, _sparkline(ppm_series)),
            _Metric("Status", "RUNNING", "", now, ""),
        ]
    return machines, latest_by_machine


def _customer_ok(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return False
    try:
        prof = user.customer_profile
    except Exception:
        return False
    return bool(prof.is_active)


def portal_login(request):
    """Customer login."""
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
    
    # FIX: Ensure CustomerDocument is imported at top
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
            # Create a new record in the database
            MachineTelemetry.objects.create(
                machine_id=data.get('machine_id'),
                ppm=data.get('ppm'),
                temp=data.get('temp'),
                batch_count=data.get('batch_count'),
                status=data.get('status')
            )
            return JsonResponse({"status": "success", "message": "Telemetry saved"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)


@require_GET
def machine_metrics_api(request):
    """
    Returns the LATEST record from the DB for the dashboard.
    """
    if not _customer_ok(request.user):
         return JsonResponse({"error": "Unauthorized"}, status=403)

    machine_id = request.GET.get('machine_id', 'i6')

    # Static config for names (can be replaced with DB lookup later)
    machines_db = {
        'i6': {'name': 'MPE i6 Tray Sealer'},
        'i3': {'name': 'MPE i3 Tray Sealer'},
        'test': {'name': 'LAB-01 Test Unit'},
    }
    config = machines_db.get(machine_id, {'name': 'Unknown Machine'})

    # --- READ FROM DB ---
    latest = MachineTelemetry.objects.filter(machine_id=machine_id).first()

    if latest:
        # Use live data from database
        return JsonResponse({
            'machine_id': machine_id,
            'name': config['name'],
            'status': latest.status,
            'metrics': {
                'ppm': latest.ppm,
                'temp': latest.temp,
                'batch': latest.batch_count,
                'utilisation': 88 if latest.status == "RUNNING" else 0
            }
        })
    else:
        # Fallback if no data sent yet
        return JsonResponse({
            'machine_id': machine_id,
            'name': config['name'],
            'status': "OFFLINE",
            'metrics': {
                'ppm': 0,
                'temp': 0,
                'batch': 0,
                'utilisation': 0
            }
        })
    

@csrf_exempt  # Allows the script to post without a browser CSRF token
def api_import_stock(request):
    """
    Receives JSON list of products from the PC App and updates the database.
    Requires Basic Authentication (Username/Password of a Staff member).
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        
        # 1. Security Check
        username = data.get('username')
        password = data.get('password')
        products_data = data.get('products', [])
        
        user = authenticate(username=username, password=password)
        if not user or not user.is_staff:
            return JsonResponse({"status": "error", "message": "Invalid credentials or not staff"}, status=403)

        # 2. Process Data
        created_count = 0
        updated_count = 0
        
        for item in products_data:
            # item = {'sku': '...', 'name': '...', 'price': 10.50, 'description': '...'}
            
            # Identify by Name (Stock Ref) as per your previous logic
            obj, created = ShopProduct.objects.update_or_create(
                name=item['name'], # Assuming 'name' is the Stock Ref
                defaults={
                    'description': item.get('description', ''),
                    'price_gbp': item.get('price', 0.0),
                    'stock_status': 'In Stock',
                    'is_active': True,
                    # 'sku': item.get('sku', '') # Optional if you want to save SKU
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1

        return JsonResponse({
            "status": "success", 
            "created": created_count, 
            "updated": updated_count
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# -----------------------------------------------------------------------------
# Shop cart + checkout (Phase 2)
# -----------------------------------------------------------------------------

def _get_cart(request) -> dict:
    """Session cart: {str(product_id): int(qty)}"""
    cart = request.session.get("cart") or {}
    # normalise
    fixed = {}
    for k, v in cart.items():
        try:
            fixed[str(int(k))] = max(0, int(v))
        except Exception:
            continue
    request.session["cart"] = fixed
    return fixed


def _cart_items(cart: dict):
    """Returns (items, total_qty)."""
    ids = [int(pid) for pid, qty in cart.items() if int(qty) > 0]
    prods = {p.id: p for p in ShopProduct.objects.filter(id__in=ids, is_active=True)}
    items = []
    total_qty = 0
    for pid_str, qty in cart.items():
        qty = int(qty)
        if qty <= 0:
            continue
        pid = int(pid_str)
        p = prods.get(pid)
        if not p:
            continue
        total_qty += qty
        items.append({
            "product": p,
            "qty": qty,
        })
    return items, total_qty


@csrf_exempt
def cart_add(request, product_id: int):
    """Add an item to the session cart."""
    if request.method not in ("POST", "GET"):
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        qty = int(request.POST.get("qty") or request.GET.get("qty") or 1)
    except Exception:
        qty = 1
    qty = max(1, min(qty, 999))

    product = get_object_or_404(ShopProduct, pk=product_id, is_active=True)
    cart = _get_cart(request)
    cart[str(product.id)] = int(cart.get(str(product.id), 0)) + qty
    request.session["cart"] = cart
    request.session.modified = True

    # JSON for AJAX, or redirect for normal clicks
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        _items, total_qty = _cart_items(cart)
        return JsonResponse({"ok": True, "cart_qty": total_qty})

    return redirect("cart_view")


@csrf_exempt
def cart_remove(request, product_id: int):
    if request.method not in ("POST", "GET"):
        return JsonResponse({"error": "Method not allowed"}, status=405)

    cart = _get_cart(request)
    cart.pop(str(int(product_id)), None)
    request.session["cart"] = cart
    request.session.modified = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        _items, total_qty = _cart_items(cart)
        return JsonResponse({"ok": True, "cart_qty": total_qty})

    return redirect("cart_view")


def cart_view(request):
    cart = _get_cart(request)
    items, total_qty = _cart_items(cart)

    # Site config controls global price visibility (B2B quote mode)
    config = SiteConfiguration.get_config() if hasattr(SiteConfiguration, "get_config") else None
    show_prices = True if not config else bool(getattr(config, "shop_show_prices", True))

    total_price = 0
    if show_prices:
        for it in items:
            p = it["product"]
            if getattr(p, "show_price", True):
                total_price += float(p.price_gbp) * it["qty"]

    ctx = {
        "items": items,
        "total_qty": total_qty,
        "show_prices": show_prices,
        "total_price": total_price,
        "background_images_json": _background_images_json() if "_background_images_json" in globals() else "[]",
    }
    return render(request, "core/cart.html", ctx)


def _prefill_checkout_initial(request):
    """Build initial data for CheckoutForm using CustomerProfile or last order."""
    initial = {}

    if request.user.is_authenticated and not request.user.is_staff:
        # Basic user details
        full_name = (request.user.get_full_name() or "").strip()
        if full_name:
            initial["name"] = full_name
        initial["email"] = (request.user.email or "").strip()

        # CustomerProfile company (if present)
        try:
            prof = request.user.customer_profile
        except Exception:
            prof = None
        if prof and getattr(prof, "company_name", ""):
            initial["company"] = prof.company_name

        # Previous order address/contact
        last = ShopOrder.objects.filter(user=request.user).order_by("-created_at").first()
        if last:
            if last.contact:
                if not initial.get("name"):
                    initial["name"] = last.contact.name
                if not initial.get("company"):
                    initial["company"] = last.contact.company
                if not initial.get("phone"):
                    initial["phone"] = last.contact.phone
                if not initial.get("email"):
                    initial["email"] = last.contact.email

            addr = last.order_addresses.first()
            if addr:
                initial.update({
                    "address_1": addr.address_1,
                    "address_2": addr.address_2,
                    "city": addr.city,
                    "county": addr.county,
                    "postcode": addr.postcode,
                    "country": addr.country,
                })

        # Saved default address for contact (if any)
        contact = CustomerContact.objects.filter(user=request.user).order_by("-updated_at").first()
        if contact:
            if not initial.get("name"):
                initial["name"] = contact.name
            if not initial.get("company"):
                initial["company"] = contact.company
            if not initial.get("phone"):
                initial["phone"] = contact.phone
            if not initial.get("email"):
                initial["email"] = contact.email

            default_addr = contact.addresses.filter(is_default=True).first()
            if default_addr and not initial.get("address_1"):
                initial.update({
                    "address_1": default_addr.address_1,
                    "address_2": default_addr.address_2,
                    "city": default_addr.city,
                    "county": default_addr.county,
                    "postcode": default_addr.postcode,
                    "country": default_addr.country,
                })

    return initial


def checkout(request):
    cart = _get_cart(request)
    items, total_qty = _cart_items(cart)
    if total_qty <= 0:
        messages.info(request, "Your basket is empty.")
        return redirect("shop")

    config = SiteConfiguration.get_config() if hasattr(SiteConfiguration, "get_config") else None
    show_prices = True if not config else bool(getattr(config, "shop_show_prices", True))
    sales_email = getattr(config, "email", None) if config else None

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # 1) Create / update contact (tie to user if authenticated)
            user = request.user if (request.user.is_authenticated and not request.user.is_staff) else None
            contact, _created = CustomerContact.objects.update_or_create(
                user=user,
                email=cd["email"],
                defaults={
                    "name": cd["name"],
                    "company": cd.get("company", ""),
                    "phone": cd.get("phone", ""),
                },
            )

            # 2) Save address + default
            addr = CustomerAddress.objects.create(
                contact=contact,
                label=cd.get("address_label") or "Delivery",
                address_1=cd["address_1"],
                address_2=cd.get("address_2", ""),
                city=cd.get("city", ""),
                county=cd.get("county", ""),
                postcode=cd.get("postcode", ""),
                country=cd.get("country", "United Kingdom"),
                is_default=True,
            )
            # (CustomerAddress.save() enforces single default)

            # 3) Create order
            order = ShopOrder.objects.create(
                user=user,
                contact=contact,
                order_number=cd.get("order_number", ""),
                notes=cd.get("notes", ""),
                status="new",
            )

            # 4) Copy address snapshot to order
            ShopOrderAddress.objects.create(
                order=order,
                label=addr.label,
                address_1=addr.address_1,
                address_2=addr.address_2,
                city=addr.city,
                county=addr.county,
                postcode=addr.postcode,
                country=addr.country,
            )

            # 5) Add items
            for it in items:
                p = it["product"]
                qty = it["qty"]
                unit_price = float(p.price_gbp) if (show_prices and getattr(p, "show_price", True)) else 0
                ShopOrderItem.objects.create(
                    order=order,
                    product=p,
                    product_name=p.name,
                    sku=p.sku or "",
                    unit_price_gbp=unit_price,
                    quantity=qty,
                )

            # 6) Clear cart
            request.session["cart"] = {}
            request.session.modified = True

            # 7) Send emails (simple, non-blocking)
            try:
                subject = f"MPE Shop Order Request #{order.id}"
                lines = [
                    f"Order ID: {order.id}",
                    f"PO / Order Number: {order.order_number or '-'}",
                    f"Name: {contact.name}",
                    f"Company: {contact.company or '-'}",
                    f"Email: {contact.email}",
                    f"Phone: {contact.phone or '-'}",
                    "",
                    "Items:",
                ]
                for it in order.items.all():
                    price_part = f"£{it.unit_price_gbp:.2f}" if show_prices and it.unit_price_gbp else "Price on request"
                    lines.append(f"- {it.product_name} x{it.quantity} ({price_part})")
                body = "\n".join(lines)

                to_emails = [contact.email]
                cc_emails = []
                if sales_email:
                    cc_emails.append(sales_email)

                email = EmailMultiAlternatives(subject=subject, body=body, to=to_emails, cc=cc_emails)
                email.send(fail_silently=True)
            except Exception:
                pass

            messages.success(request, "Order submitted. We'll be in touch shortly.")
            return redirect("shop")

    else:
        form = CheckoutForm(initial=_prefill_checkout_initial(request))

    ctx = {
        "form": form,
        "items": items,
        "total_qty": total_qty,
        "show_prices": show_prices,
        "background_images_json": _background_images_json() if "_background_images_json" in globals() else "[]",
    }
    return render(request, "core/checkout.html", ctx)


def portal_orders(request):
    """Logged-in customer order history."""
    if not _customer_ok(request.user):
        return redirect(f"{reverse('portal_login')}?next={reverse('portal_orders')}")
    orders = (
        ShopOrder.objects.filter(user=request.user)
        .select_related("contact")
        .prefetch_related("items", "order_addresses")
        .order_by("-created_at")
    )
    ctx = {"orders": orders, "background_images_json": _background_images_json()}
    return render(request, "core/portal_orders.html", ctx)
