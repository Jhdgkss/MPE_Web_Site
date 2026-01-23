from django import forms

from .models import SiteConfiguration


class SiteConfigurationForm(forms.ModelForm):
    """Staff-friendly editor for homepage + site-wide configuration."""

    class Meta:
        model = SiteConfiguration
        fields = [
            # Branding
            "logo",

            # Hero
            "hero_title",
            "hero_subtitle",
            "hero_description",
            "hero_image",
            "hero_button_text",
            "hero_button_link",

            # Feature bullets
            "feature_1",
            "feature_2",
            "feature_3",

            # Contact
            "phone_number",
            "email",
            "location",

            # Social
            "linkedin_url",
            "facebook_url",
            "youtube_url",
        ]

        widgets = {
            "hero_description": forms.Textarea(attrs={"rows": 4}),
            "hero_button_link": forms.TextInput(
                attrs={
                    "placeholder": "#machines or /shop/ or https://...",
                    "autocomplete": "off",
                }
            ),
        }
