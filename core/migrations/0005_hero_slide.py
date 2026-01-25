from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_siteconfiguration"),
    ]

    operations = [
        migrations.CreateModel(
            name="HeroSlide",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("subtitle", models.CharField(blank=True, max_length=180)),
                ("body", models.TextField(blank=True)),
                ("cta_text", models.CharField(blank=True, max_length=50)),
                ("cta_link", models.CharField(blank=True, help_text="Internal path or full URL", max_length=240)),
                ("kind", models.CharField(choices=[("image", "Image"), ("embed", "Embedded video (URL)")], default="image", max_length=12)),
                ("image", models.ImageField(blank=True, null=True, upload_to="hero_slides/")),
                ("embed_url", models.URLField(blank=True, help_text="YouTube/Vimeo embed URL")),
                ("bullet_1", models.CharField(blank=True, max_length=120)),
                ("bullet_2", models.CharField(blank=True, max_length=120)),
                ("bullet_3", models.CharField(blank=True, max_length=120)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["sort_order", "created_at"],
            },
        ),
    ]
