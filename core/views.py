from django.shortcuts import render
from .models import SiteConfiguration

def home(request):
    # Try to get the first configuration object from the database
    config = SiteConfiguration.objects.first()
    
    # Fallback if no configuration exists in the DB yet
    if not config:
        # Create a temporary object (not saved to DB) just for display
        config = SiteConfiguration(
            site_name="Default Site Name", 
            welcome_message="Please go to /admin to configure your site settings.",
            background_color="#f0f0f0"
        )
    
    return render(request, 'home.html', {'config': config})