# MPE Restore Main Styling + Isolated Dashboard CSS (Patch)

## What this fixes
- Restores the site's main styling by restoring the *original* `templates/base.html` and `static/styles.css`
- Keeps dashboard styling separate in `static/dashboard.css`
- Loads `dashboard.css` ONLY on the metrics dashboard page via `{% block extra_head %}`

## Files in this patch
- templates/base.html
- static/styles.css
- static/dashboard.css
- templates/core/portal_dashboard.html

## Apply
Copy the folders from this zip into your project root (merge/overwrite when prompted), then run:

```bash
python manage.py runserver
```

No migrations. Railway-safe.
