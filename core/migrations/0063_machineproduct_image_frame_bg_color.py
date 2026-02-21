from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0062_fix_legacy_machineproduct_hero_heading_default"),
    ]

    operations = [
        migrations.AddField(
            model_name="machineproduct",
            name="image_frame_bg_color",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Background colour for the machine image frame (e.g. #ffffff). Leave blank to use default.",
                max_length=32,
            ),
        ),
    ]
