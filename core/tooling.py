from django.shortcuts import render

def tooling(request):
    """Tooling landing page.

    Renders admin-driven tooling content when available (ToolingPage / ToolingFeature / ToolingGalleryImage),
    otherwise falls back to a safe minimal layout.
    """
    context = {}

    # Try to load optional models (added by the admin-editable tooling patch).
    try:
        from .models import ToolingPage, ToolingFeature, ToolingGalleryImage  # type: ignore
        tooling_page = ToolingPage.objects.first()
        context["tooling_page"] = tooling_page

        # Feature cards (e.g., Custom Tooling / Spares & Parts)
        features_qs = ToolingFeature.objects.all()
        # Support optional fields if present
        if hasattr(ToolingFeature, "is_active"):
            features_qs = features_qs.filter(is_active=True)
        if hasattr(ToolingFeature, "sort_order"):
            features_qs = features_qs.order_by("sort_order", "id")
        else:
            features_qs = features_qs.order_by("id")
        context["tooling_features"] = list(features_qs)

        # Gallery images (optional section)
        gallery_qs = ToolingGalleryImage.objects.all()
        if hasattr(ToolingGalleryImage, "is_active"):
            gallery_qs = gallery_qs.filter(is_active=True)
        if hasattr(ToolingGalleryImage, "sort_order"):
            gallery_qs = gallery_qs.order_by("sort_order", "id")
        else:
            gallery_qs = gallery_qs.order_by("id")
        context["tooling_gallery_images"] = list(gallery_qs)

    except Exception:
        # If models don't exist in this deployment, keep template rendering safe.
        context.setdefault("tooling_page", None)
        context.setdefault("tooling_features", [])
        context.setdefault("tooling_gallery_images", [])

    return render(request, "core/tooling.html", context)
