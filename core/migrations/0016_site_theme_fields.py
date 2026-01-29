from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_distributor"),
    ]

    operations = [
        # NOTE:
        # All fields that were originally added here already exist in the
        # production PostgreSQL database (Railway).
        #
        # Attempting to re-add them causes errors like:
        #   psycopg2.errors.DuplicateColumn:
        #   column "default_theme" / "show_theme_toggle" already exists
        #
        # This migration is therefore intentionally left as a NO-OP.
        # The schema is already correct; this only aligns Django's
        # migration history with the real database state.
    ]
