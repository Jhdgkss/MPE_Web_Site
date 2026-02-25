from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0063_machineproduct_image_frame_bg_color"),
    ]

    operations = [
        migrations.CreateModel(
            name="ToolingPage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hero_title", models.CharField(blank=True, default="Tooling Solutions", max_length=120)),
                (
                    "hero_subtitle",
                    models.CharField(
                        blank=True,
                        default="Bespoke tooling and spares for your packaging machinery.",
                        max_length=220,
                    ),
                ),
                (
                    "intro_heading",
                    models.CharField(blank=True, default="Tooling for your tray or pack format", max_length=120),
                ),
                (
                    "intro_text",
                    models.TextField(
                        blank=True,
                        default=(
                            "Tooling is the change-part set that fits into your sealing machine to match a specific tray, "
                            "film, or packaging format. We design and manufacture robust, repeatable tooling solutions "
                            "to suit your product, throughput, and changeover requirements."
                        ),
                    ),
                ),
                ("gallery_heading", models.CharField(blank=True, default="Tooling examples", max_length=120)),
                ("features_heading", models.CharField(blank=True, default="How we can help", max_length=120)),
                (
                    "hero_image",
                    models.ImageField(
                        blank=True,
                        help_text="Optional hero image for the tooling page.",
                        null=True,
                        upload_to="tooling/hero/",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tooling page",
                "verbose_name_plural": "Tooling page",
            },
        ),
        migrations.CreateModel(
            name="ToolingFeature",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("title", models.CharField(max_length=80)),
                ("description", models.TextField(blank=True)),
                (
                    "icon_class",
                    models.CharField(
                        blank=True,
                        help_text="Optional FontAwesome class, e.g. fa-solid fa-gear",
                        max_length=80,
                    ),
                ),
                ("image", models.ImageField(blank=True, null=True, upload_to="tooling/features/")),
                ("button_text", models.CharField(blank=True, max_length=40)),
                (
                    "button_url",
                    models.CharField(
                        blank=True,
                        help_text="URL or path (e.g. /contact/ or https://...)",
                        max_length=240,
                    ),
                ),
                (
                    "button_style",
                    models.CharField(
                        choices=[("primary", "Primary"), ("ghost", "Ghost")],
                        default="ghost",
                        max_length=12,
                    ),
                ),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="features",
                        to="core.toolingpage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tooling feature",
                "verbose_name_plural": "Tooling features",
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="ToolingGalleryImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("image", models.ImageField(upload_to="tooling/gallery/")),
                ("caption", models.CharField(blank=True, max_length=120)),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="gallery",
                        to="core.toolingpage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tooling gallery image",
                "verbose_name_plural": "Tooling gallery images",
                "ordering": ["sort_order", "id"],
            },
        ),
    ]
