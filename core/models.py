from django.db import models

class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=200, default="My Website")
    welcome_message = models.TextField(default="Welcome to our site!")
    # Stores a hex color code (e.g., #FFFFFF)
    background_color = models.CharField(max_length=7, default="#ffffff", help_text="Hex code like #ffffff")

    def __str__(self):
        return "Website Configuration"

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"