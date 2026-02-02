from django.db import migrations, models
from django.utils.text import slugify


def populate_shopproduct_slugs(apps, schema_editor):
    ShopProduct = apps.get_model("core", "ShopProduct")
    existing = set(ShopProduct.objects.exclude(slug__isnull=True).exclude(slug__exact="").values_list("slug", flat=True))

    for p in ShopProduct.objects.all().order_by("id"):
        if p.slug:
            continue

        base = slugify(p.name)[:150] or "product"
        slug = base
        i = 2
        while slug in existing or ShopProduct.objects.filter(slug=slug).exclude(pk=p.pk).exists():
            slug = f"{base}-{i}"
            i += 1

        p.slug = slug
        p.save(update_fields=["slug"])
        existing.add(slug)


class Migration(migrations.Migration):

    dependencies = [
    ('core', '0040_shop_basket_and_orders'),
    ]


    operations = [
        migrations.AddField(
            model_name="shopproduct",
            name="slug",
            field=models.SlugField(blank=True, help_text="SEO-friendly URL slug (auto-generated if blank)", max_length=160, unique=True),
        ),
        migrations.AddField(
            model_name="shopproduct",
            name="specifications",
            field=models.JSONField(blank=True, default=dict, help_text="Key/value specs shown on the product page (e.g. {'Voltage':'230V','Material':'Stainless'})", null=True),
        ),
        migrations.RunPython(populate_shopproduct_slugs, migrations.RunPython.noop),
    ]
