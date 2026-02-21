from django.db import migrations


def fix_legacy_hero_heading(apps, schema_editor):
    """Railway/Postgres: some older DBs still have legacy columns (hero_heading/hero_subheading)
    that are NOT NULL with no DEFAULT, which breaks INSERTs from the newer model that uses
    hero_title/hero_subtitle.

    This migration makes legacy columns safe by setting a DEFAULT '' (and backfilling NULLs)
    if those columns exist.

    Safe on SQLite and safe if the columns don't exist.
    """

    if schema_editor.connection.vendor != "postgresql":
        return

    # Postgres: conditionally set defaults only if the columns exist
    schema_editor.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'core_machineproduct'
                  AND column_name = 'hero_heading'
            ) THEN
                EXECUTE 'UPDATE core_machineproduct SET hero_heading = '''' WHERE hero_heading IS NULL;';
                EXECUTE 'ALTER TABLE core_machineproduct ALTER COLUMN hero_heading SET DEFAULT '''''';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'core_machineproduct'
                  AND column_name = 'hero_subheading'
            ) THEN
                EXECUTE 'UPDATE core_machineproduct SET hero_subheading = '''' WHERE hero_subheading IS NULL;';
                EXECUTE 'ALTER TABLE core_machineproduct ALTER COLUMN hero_subheading SET DEFAULT '''''';
            END IF;
        END $$;
        """
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0061_fix_machineproductvideo_columns"),
    ]

    operations = [
        migrations.RunPython(fix_legacy_hero_heading, migrations.RunPython.noop),
    ]
