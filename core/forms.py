from django import forms
from .models import SiteConfiguration

class SiteConfigurationForm(forms.ModelForm):
    """Staff-friendly editor for homepage + site-wide configuration."""

    class Meta:
        model = SiteConfiguration
        fields = [
            # Branding
            "logo",

            # Contact
            "phone_number",
            "email",
            "location",

            # Social
            "linkedin_url",
            "facebook_url",
            "youtube_url",

            # Features
            "feature_1",
            "feature_2",
            "feature_3",
        ]
        # Removed Hero fields from here