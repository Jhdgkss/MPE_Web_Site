"""
Context processors to inject data into all templates
"""
from .models import SiteConfiguration, StyleOverride


def site_config(request):
    """Make site configuration available to all templates

    Some branches of this project previously used a `SiteConfiguration.get_config()`
    classmethod. If that method is missing (e.g. after a migration/model edit),
    fall back to a safe singleton `get_or_create(pk=1)`.
    """
    get_config = getattr(SiteConfiguration, "get_config", None)

    if callable(get_config):
        config = get_config()
    else:
        config, _ = SiteConfiguration.objects.get_or_create(pk=1)

    # Page/section style overrides (optional)
    url_name = ""
    try:
        rm = getattr(request, "resolver_match", None)
        if rm and getattr(rm, "url_name", None):
            url_name = str(rm.url_name)
    except Exception:
        url_name = ""

    page_overrides = []
    section_overrides = []
    try:
        qs = StyleOverride.objects.filter(is_active=True)
        if url_name:
            page_overrides = list(qs.filter(scope=StyleOverride.SCOPE_PAGE, page_url_name=url_name).order_by("sort_order", "name"))
        section_overrides = list(qs.filter(scope=StyleOverride.SCOPE_SECTION).order_by("sort_order", "name"))
    except Exception:
        # Safe fallback if migrations not yet applied
        page_overrides = []
        section_overrides = []

    return {
        "site_config": config,
        "page_style_overrides": page_overrides,
        "section_style_overrides": section_overrides,
        "current_url_name": url_name,
    }
