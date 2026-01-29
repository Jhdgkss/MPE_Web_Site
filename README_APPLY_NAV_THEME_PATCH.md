MPE Nav / Theme Admin Patch (29 Jan 2026)

What this patch adds
- Admin-controlled navbar colours (light/dark) + link colours
- Per-navbar-link colour overrides via JSON
- Separate logo images for light vs dark theme (logo_light / logo_dark)
- Optional theme toggle button in header (stored in localStorage)
- Animated, more colourful nav buttons and primary CTA button
- Dashboard colours follow the theme variables

How to apply
1) Unzip and copy the folders into your Django project root, overwriting:
   - core/models.py
   - core/admin.py
   - core/migrations/0016_site_theme_navbar.py
   - templates/base.html
   - static/styles.css
   - static/dashboard.css

2) Run migrations:
   python manage.py migrate

3) In Django Admin:
   Admin -> Site Configuration
   - Upload logo_light and logo_dark (optional)
   - Set navbar backgrounds + default link colours
   - (Optional) set per-link colours in nav_item_colours JSON

Per-link colours JSON example:
{
  "home": "#2f7d32",
  "machines": "#0ea5e9",
  "tooling": "#8b5cf6",
  "shop": "#f59e0b",
  "customer": "#10b981",
  "admin": "#ef4444",
  "quote": "#2f7d32"
}

Notes
- If you don't set a per-link colour, the default nav_link_* colours are used.
- The GET A QUOTE button uses the 'quote' colour if provided, else btn_primary.
- Theme toggle: shown only if show_theme_toggle = True.
