from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0044_fix_shopproduct_slugs"),
    ]

    operations = [
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
