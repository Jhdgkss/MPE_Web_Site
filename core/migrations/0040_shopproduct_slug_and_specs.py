from django.db import migrations, models
from django.utils.text import slugify


def forwards(apps, schema_editor):
    ShopProduct = apps.get_model("core", "ShopProduct")

    # Collect existing non-empty slugs so we can enforce uniqueness
    existing = set(
        ShopProduct.objects.exclude(slug__isnull=True)
        .exclude(slug="")
        .values_list("slug", flat=True)
    )

    for p in ShopProduct.objects.all().order_by("id"):
        base = slugify(p.name)[:150] or "product"
        slug = (p.slug or "").strip()

        # Generate if missing OR duplicated
        if (not slug) or (slug in existing):
            candidate = base
            i = 2
            while candidate in existing:
                candidate = f"{base}-{i}"
                i += 1
            slug = candidate

        existing.add(slug)

        if p.slug != slug:
            p.slug = slug
            p.save(update_fields=["slug"])


def backwards(apps, schema_editor):
    # don't undo slugs
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0039_remove_distributor_cta_text"),
    ]

    operations = [
        # If specifications doesn't exist yet, add it
        migrations.AddField(
            model_name="shopproduct",
            name="specifications",
            field=models.JSONField(blank=True, null=True, default=dict),
        ),

        # Fix/populate slugs BEFORE enforcing unique
        migrations.RunPython(forwards, backwards),

        # Enforce unique now that data is clean
        migrations.AlterField(
            model_name="shopproduct",
            name="slug",
            field=models.SlugField(
                max_length=160,
                unique=True,
                blank=True,
                help_text="SEO-friendly URL slug (auto-generated if blank)",
            ),
        ),
    ]
