from django.db import migrations
from django.utils.text import slugify


def fix_slugs(apps, schema_editor):
    ShopProduct = apps.get_model("core", "ShopProduct")

    existing = set(
        ShopProduct.objects
        .exclude(slug__isnull=True)
        .exclude(slug="")
        .values_list("slug", flat=True)
    )

    for product in ShopProduct.objects.all().order_by("id"):
        slug = (product.slug or "").strip()

        if not slug or slug in existing:
            base = slugify(product.name)[:150] or "product"
            candidate = base
            i = 2
            while candidate in existing:
                candidate = f"{base}-{i}"
                i += 1
            slug = candidate

        existing.add(slug)

        if product.slug != slug:
            product.slug = slug
            product.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0043_add_user_links"),
    ]

    operations = [
        migrations.RunPython(fix_slugs, migrations.RunPython.noop),
    ]
