import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import (
    BackgroundImage,
    MachineProduct,
    ShopProduct,
    CustomerDocument,
    CustomerMachine,
    MachineMetric,
    StaffDocument,
)


def _background_images_json() -> str:
    imgs = BackgroundImage.objects.filter(is_active=True)
    urls = [img.image.url for img in imgs if img.image]
    return json.dumps(urls)


def index(request):
    machines = MachineProduct.objects.filter(is_active=True)
    ctx = {
        "machines": machines,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/index.html", ctx)


def shop(request):
    # Products are loaded via JS from /api/products/
    ctx = {
        "background_images_json": _background_images_json(),
        "page_title": "Shop",
        "page_heading": "Spares Shop",
        "page_intro": "Order common spares and consumables. More parts will be added over time.",
        "initial_category": "",
    }
    return render(request, "core/shop.html", ctx)


def tooling(request):
    # Same catalogue, but pre-filtered to tooling category
    ctx = {
        "background_images_json": _background_images_json(),
        "page_title": "Tooling",
        "page_heading": "Tooling",
        "page_intro": "Browse tooling-related items. If you can't find what you need, contact us.",
        "initial_category": "tooling",
    }
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
                "price": float(p.price_gbp),
                "image_url": p.image.url if p.image else "",
                "stock_status": "In Stock" if p.in_stock else "Out of Stock",
                "created_at": p.created_at.isoformat(),
            }
        )
    return JsonResponse(data, safe=False)


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
# Customer Portal (login required)
# -----------------------------------------------------------------------------

def portal_login(request):
    if request.user.is_authenticated:
        return redirect("portal_home")

    next_url = request.GET.get("next") or reverse("portal_home")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Login failed. Please check your username and password.")
        else:
            login(request, user)
            return redirect(request.POST.get("next") or next_url)

    ctx = {
        "next": next_url,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/portal_login.html", ctx)


def portal_logout(request):
    logout(request)
    return redirect("index")


@login_required(login_url="portal_login")
def portal_home(request):
    docs = CustomerDocument.objects.filter(customer=request.user, is_active=True)[:8]
    machines = CustomerMachine.objects.filter(customer=request.user, is_active=True)
    ctx = {
        "docs": docs,
        "machines": machines,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/portal_home.html", ctx)


@login_required(login_url="portal_login")
def portal_documents(request):
    docs = CustomerDocument.objects.filter(customer=request.user, is_active=True)
    ctx = {
        "docs": docs,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/portal_documents.html", ctx)


@login_required(login_url="portal_login")
def portal_dashboard(request):
    machines = CustomerMachine.objects.filter(customer=request.user, is_active=True)

    # Latest metrics per machine/metric_key (simple approach):
    # 1) Find latest timestamps per machine+key
    latest = (
        MachineMetric.objects
        .filter(machine__in=machines)
        .values("machine_id", "metric_key")
        .annotate(latest_ts=Max("timestamp"))
    )

    # 2) Pull the actual rows
    latest_rows = []
    for row in latest:
        m = MachineMetric.objects.filter(
            machine_id=row["machine_id"],
            metric_key=row["metric_key"],
            timestamp=row["latest_ts"]
        ).first()
        if m:
            latest_rows.append(m)

    # Group by machine
    by_machine = {}
    for m in latest_rows:
        by_machine.setdefault(m.machine_id, []).append(m)

    ctx = {
        "machines": machines,
        "latest_metrics_by_machine": by_machine,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/portal_dashboard.html", ctx)


# -----------------------------------------------------------------------------
# Staff area (separate from Django Admin)
# -----------------------------------------------------------------------------

def _is_staff(user):
    return user.is_authenticated and user.is_staff


def staff_login(request):
    """Staff login page (uses Django auth, but not the /admin UI)."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("staff_home")

    next_url = request.GET.get("next") or reverse("staff_home")

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

    ctx = {
        "next": next_url,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/staff_login.html", ctx)


def staff_logout(request):
    logout(request)
    return redirect("index")


@user_passes_test(_is_staff, login_url="staff_login")
def staff_home(request):
    docs = StaffDocument.objects.filter(is_active=True)
    ctx = {
        "docs": docs,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/staff_home.html", ctx)
