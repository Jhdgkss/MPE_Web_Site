from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0027_merge_20260129_2147"),
    ]

    operations = [
        migrations.CreateModel(
            name="StyleOverride",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Friendly name shown in Admin", max_length=80)),
                (
                    "scope",
                    models.CharField(
                        choices=[("page", "Page"), ("section", "Section")],
                        default="page",
                        max_length=12,
                    ),
                ),
                (
                    "page_url_name",
                    models.CharField(
                        blank=True,
                        help_text="For Page scope: Django URL name (e.g. index, machines, tooling, shop, contact).",
                        max_length=80,
                    ),
                ),
                (
                    "section_key",
                    models.CharField(
                        blank=True,
                        help_text="For Section scope: data-section key (e.g. hero, machines, distributors, cta, footer).",
                        max_length=80,
                    ),
                ),
                ("site_bg_color", models.CharField(blank=True, max_length=32)),
                ("site_text_color", models.CharField(blank=True, max_length=32)),
                ("primary_color", models.CharField(blank=True, max_length=32)),
                ("secondary_color", models.CharField(blank=True, max_length=32)),
                ("link_color", models.CharField(blank=True, max_length=32)),
                ("topbar_bg_color", models.CharField(blank=True, max_length=32)),
                ("topbar_text_color", models.CharField(blank=True, max_length=32)),
                ("header_bg_color", models.CharField(blank=True, max_length=32)),
                ("header_text_color", models.CharField(blank=True, max_length=32)),
                ("hero_bg_color", models.CharField(blank=True, max_length=32)),
                ("hero_text_color", models.CharField(blank=True, max_length=32)),
                ("hero_box_bg_color", models.CharField(blank=True, max_length=32)),
                ("hero_box_bg_opacity", models.PositiveSmallIntegerField(blank=True, help_text="0-100 (%)", null=True)),
                ("section_alt_bg_color", models.CharField(blank=True, max_length=32)),
                ("machines_section_bg_color", models.CharField(blank=True, max_length=32)),
                ("machines_section_text_color", models.CharField(blank=True, max_length=32)),
                ("distributors_section_bg_color", models.CharField(blank=True, max_length=32)),
                ("distributors_section_text_color", models.CharField(blank=True, max_length=32)),
                ("card_bg_color", models.CharField(blank=True, max_length=32)),
                ("card_text_color", models.CharField(blank=True, max_length=32)),
                ("footer_bg_color", models.CharField(blank=True, max_length=32)),
                ("footer_text_color", models.CharField(blank=True, max_length=32)),
                ("footer_link_color", models.CharField(blank=True, max_length=32)),
                (
                    "custom_css",
                    models.TextField(
                        blank=True,
                        help_text="Optional: small CSS snippet applied after variables.",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Style Override",
                "verbose_name_plural": "Style Overrides",
                "ordering": ["sort_order", "name"],
            },
        ),
    ]
