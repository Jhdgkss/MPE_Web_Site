import json
import random
from collections import namedtuple
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# UPDATED IMPORTS: Added CustomerDocument and CustomerMachine
from .models import (
    BackgroundImage, HeroSlide, MachineProduct, ShopProduct, SiteConfiguration,
    CustomerProfile, MachineTelemetry, Distributor, CustomerDocument, CustomerMachine
)
from .forms import SiteConfigurationForm


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