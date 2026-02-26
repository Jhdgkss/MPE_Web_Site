from django.shortcuts import render


def tooling(request):
    """Tooling landing page.

    Purpose:
    - Gives you a stable /tooling/ route today (for Railway + links)
    - Later becomes the entry point for a tooling specification generator form

    No database changes. No dependencies.
    """
    # Keep this view resilient.
    # If the optional admin-driven tooling models exist, load them.
    # If not, the page still renders with defaults.
    ctx = {}

    try:
        from .models import ToolingPage, ToolingFeature, ToolingGalleryImage  # type: ignore

        ctx["tooling_page"] = ToolingPage.objects.first()
        ctx["tooling_features"] = ToolingFeature.objects.all()
        ctx["tooling_gallery"] = ToolingGalleryImage.objects.all()
    except Exception:
        pass

    return render(request, "core/tooling.html", ctx)
