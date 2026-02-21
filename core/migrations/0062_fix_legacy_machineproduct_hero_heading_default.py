from django.db import migrations


def fix_legacy_hero_columns(apps, schema_editor):
    """
    Railway/Postgres only.

    Some older deployments had legacy columns 'hero_heading' and/or 'hero_subheading'
    on core_machineproduct with NOT NULL constraints. Newer code may no longer use
    those fields, but the DB constraint can still block inserts during JSON import.

    This migration:
      - checks if the legacy columns exist
      - sets any NULLs to empty string
      - sets a DEFAULT empty string so future inserts don't fail
    """
    if schema_editor.connection.vendor != "postgresql":
        return

    table = "core_machineproduct"
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            '''
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
              AND column_name IN ('hero_heading', 'hero_subheading')
            ''',
            [table],
        )
        cols = {row[0] for row in cursor.fetchall()}

        if "hero_heading" in cols:
            cursor.execute("UPDATE \"core_machineproduct\" SET \"hero_heading\" = '' WHERE \"hero_heading\" IS NULL;")
            cursor.execute("ALTER TABLE \"core_machineproduct\" ALTER COLUMN \"hero_heading\" SET DEFAULT ''::text;")

        if "hero_subheading" in cols:
            cursor.execute("UPDATE \"core_machineproduct\" SET \"hero_subheading\" = '' WHERE \"hero_subheading\" IS NULL;")
            cursor.execute("ALTER TABLE \"core_machineproduct\" ALTER COLUMN \"hero_subheading\" SET DEFAULT ''::text;")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0061_fix_machineproductvideo_columns"),
    ]

    operations = [
        migrations.RunPython(fix_legacy_hero_columns, migrations.RunPython.noop),
    ]
