MPE Admin-Controlled Theme + Light/Dark Toggle + Colourful Buttons (Patch)

What this patch does
- Adds theme/styling fields to the existing core.SiteConfiguration (admin configurable)
- Adds a new migration (0016_site_theme_fields)
- Updates templates/base.html to:
  - Inject admin-driven CSS variables
  - Enable light/dark theme switching (toggle in header)
  - Persist user choice in localStorage
  - Add cache-busting to styles.css so changes show immediately
  - Allow disabling animations via admin (animate_buttons)
- Updates static/styles.css and static/dashboard.css to support light/dark themes and colourful buttons

Files included
- core/models.py
- core/admin.py
- core/migrations/0016_site_theme_fields.py
- templates/base.html
- static/styles.css
- static/dashboard.css

How to apply
1) Copy the folders from this zip into your project root (overwrite when prompted)
2) Run migrations:
   python manage.py migrate
3) Go to Admin -> Site Configuration and set your colours:
   - bg_light / bg_dark
   - surface_light / surface_dark
   - accent / accent_2
   - btn_primary / btn_secondary / btn_warning / btn_danger
   - default_theme (auto/light/dark)
   - show_theme_toggle (on/off)
   - animate_buttons (on/off)

Notes
- The theme toggle uses localStorage key: 'theme'
- If default_theme is set to 'auto', the first load follows browser preference.
