MPE Admin-controlled Theme + Dark/Light + Animated Buttons (Patch)

What this patch does
- Adds theme/styling fields to Core -> Site Configuration (admin-controlled)
- Adds light/dark mode support with an optional header toggle (visitor choice persists in their browser)
- Makes buttons more colourful (gradient + hover/press feedback)
- Updates dashboard CSS to match the same theme colours

Files included
- core/models.py
- core/admin.py
- core/migrations/0016_site_theme_fields.py
- templates/base.html
- static/styles.css
- static/dashboard.css

How to apply
1) Unzip this patch.
2) Copy the folders (core/, templates/, static/) into your project root, overwriting when prompted.
3) Run the migration:
     python manage.py migrate
4) Open Django Admin -> Site Configuration and set your colours:
   - Default Theme: Light/Dark/Auto
   - Show Theme Toggle: on/off
   - bg_light/bg_dark
   - surface_light/surface_dark
   - accent/accent_2
   - btn_primary/btn_secondary/btn_warning/btn_danger
   - animate_buttons: on/off

Notes
- The main CSS is cache-busted in base.html (?v=20260129a). If you later change styles.css, bump that string.
- If you have a user’s theme stuck, they can clear it by deleting localStorage key "theme" in the browser.
