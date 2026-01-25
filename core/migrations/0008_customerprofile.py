from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_merge_0005_hero_slide_0006_rename_core_metric"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("company_name", models.CharField(blank=True, max_length=160)),
                ("is_active", models.BooleanField(default=True, help_text="Disable to block portal access without deleting the user.")),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="customer_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["company_name", "user__username"],
            },
        ),
    ]
