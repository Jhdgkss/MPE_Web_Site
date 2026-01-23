"""
Context processors to inject data into all templates
"""
from .models import SiteConfiguration


def site_config(request):
    """Make site configuration available to all templates"""
    return {
        'site_config': SiteConfiguration.get_config()
    }
