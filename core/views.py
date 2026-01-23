import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET

from .models import BackgroundImage, MachineProduct, ShopProduct


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
# Staff area (separate from Django Admin)
# -----------------------------------------------------------------------------

def staff_login(request):
    """Staff login page (uses Django auth, but not the /admin UI)."""
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

    ctx = {
        "next": next_url,
        "background_images_json": _background_images_json(),
    }
    return render(request, "core/staff_login.html", ctx)


def staff_logout(request):
    logout(request)
    return redirect("index")


def staff_dashboard(request):
    """Simple staff dashboard placeholder for documents/forms."""
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect(f"{reverse('staff_login')}?next={reverse('staff_dashboard')}")

    ctx = {"background_images_json": _background_images_json()}
    return render(request, "core/staff_dashboard.html", ctx)
