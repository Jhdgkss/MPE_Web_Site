from django.shortcuts import render

from .models import ToolingPage, ToolingFeature, ToolingGalleryImage


def tooling(request):
    """Tooling landing page (editable from Admin)."""

    page = ToolingPage.get_page()

    # If no features exist yet, provide sensible defaults so the page never looks empty.
    features = list(ToolingFeature.objects.filter(page=page).order_by("sort_order", "id"))
    if not features:
        features = [
            ToolingFeature(
                page=page,
                sort_order=10,
                title="Tooling Spec Generator",
                description=(
                    "Coming soon: enter your tray details and machine model and generate a clear tooling spec for quotation."
                ),
                icon_class="fa-solid fa-calculator",
                button_text="Register Interest",
                button_url="/contact/",
                button_style=ToolingFeature.STYLE_PRIMARY,
            ),
            ToolingFeature(
                page=page,
                sort_order=20,
                title="Custom Tooling",
                description="Send us your tray drawing (or dimensions) and we’ll advise the best tooling arrangement.",
                icon_class="fa-solid fa-pen-ruler",
                button_text="Contact Us",
                button_url="/contact/",
                button_style=ToolingFeature.STYLE_GHOST,
            ),
            ToolingFeature(
                page=page,
                sort_order=30,
                title="Spares & Parts",
                description="Browse common spares and change parts.",
                icon_class="fa-solid fa-gear",
                button_text="Go to Shop",
                button_url="/shop/",
                button_style=ToolingFeature.STYLE_GHOST,
            ),
        ]

    gallery = list(ToolingGalleryImage.objects.filter(page=page).order_by("sort_order", "id"))

    return render(
        request,
        "core/tooling.html",
        {
            "tooling_page": page,
            "tooling_features": features,
            "tooling_gallery": gallery,
        },
    )
