Railway no-shell fix patch
==========================

What this fixes
--------------
Your Railway deployment is failing with:
  column core_machineproduct.hero_title does not exist

That means the Postgres database is missing columns that your code expects.

This patch:
1) Adds a DB-only migration core/0058_railway_fix_missing_machineproduct_hero_cols.py
   - Runs ONLY on Postgres (Railway)
   - Adds hero_title + hero_subtitle if missing
   - Safe to run even if columns already exist

2) Adds/updates Procfile to ensure Railway runs migrations on deploy:
   release: python manage.py migrate

How to apply
------------
1) Extract this zip into your project root (same folder as manage.py), overwrite if prompted.
2) Commit and push:

   git add core/migrations/0058_railway_fix_missing_machineproduct_hero_cols.py Procfile
   git commit -m "Railway: ensure migrations run + patch missing MachineProduct hero columns"
   git push origin main

3) Redeploy will run migrations automatically.

Notes
-----
- If you already have a Procfile with different gunicorn module, keep yours and only copy the 'release:' line.
- This patch assumes your Django project module is: myproject (myproject/wsgi.py).
