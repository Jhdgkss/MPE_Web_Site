"""
Context processors to inject data into all templates
"""
from .models import SiteConfiguration


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

    return {"site_config": config}
