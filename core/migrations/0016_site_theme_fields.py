from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_distributor"),
    ]

    operations = [
        # NOTE:
        # Railway/Postgres already has the column "default_theme" on core_siteconfiguration
        # so attempting to add it again causes:
        # psycopg2.errors.DuplicateColumn: column "default_theme" ... already exists
        #
        # Therefore we intentionally do NOT add default_theme in this migration.
        # The model field can still exist; the DB column is already present.

        migrations.AddField(
            model_name="siteconfiguration",
            name="show_theme_toggle",
            field=models.BooleanField(
                default=True,
                help_text="Show a theme toggle in the website header so visitors can switch light/dark.",
            ),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="bg_light",
            field=models.CharField(default="#f5f7f6", help_text="Site background (light mode)", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="bg_dark",
            field=models.CharField(default="#0f1115", help_text="Site background (dark mode)", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="surface_light",
            field=models.CharField(default="#ffffff", help_text="Cards/header background (light)", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="surface_dark",
            field=models.CharField(default="#171a22", help_text="Cards/header background (dark)", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="accent",
            field=models.CharField(default="#1f7a3a", help_text="Primary accent (e.g., PAL-style green)", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="accent_2",
            field=models.CharField(default="#2ea043", help_text="Accent hover/gradient partner", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="btn_primary",
            field=models.CharField(default="#1f7a3a", help_text="Primary button colour", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="btn_secondary",
            field=models.CharField(default="#0ea5e9", help_text="Secondary button colour", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="btn_warning",
            field=models.CharField(default="#f59e0b", help_text="Warning button colour", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="btn_danger",
            field=models.CharField(default="#ef4444", help_text="Danger button colour", max_length=20),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="animate_buttons",
            field=models.BooleanField(
                default=True,
                help_text="Enable subtle hover animations and press feedback on buttons."
            ),
        ),
    ]
