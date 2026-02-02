from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0039_remove_distributor_cta_text"),
    ]

    operations = [
        # Operations removed to fix DuplicateColumn error.
        # These columns were already added by 0041_merge_20260202_2121.py
    ]