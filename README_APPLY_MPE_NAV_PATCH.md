MPE NAV PATCH (Keeps your existing header formatting)

Goal:
- Remove "Distribution" from the top navbar
- Add "Customer" and "Admin" dropdowns exactly as in your diagram
- KEEP your existing header markup (logo, phone/email strip, button styling)

This patch DOES NOT overwrite your real base.html, because overwriting removed your styling before.

Files included:
- templates/snippets/mpe_nav_items.html  (copy into your existing navbar menu list)
- static/mpe_nav_dropdowns.css           (optional dropdown CSS)

HOW TO APPLY (5 minutes):
1) Find the REAL base template (the one that contains your logo + phone/email strip).
   In Cursor/VSCode: Ctrl+Shift+F and search for:  "+44 1663"  or  "sales@mpe-uk.com"  or  "GET A QUOTE"
   Open that file.

2) Inside that file, find the menu items list (example):
     <ul class="nav-menu"> ... </ul>
   or:
     <ul class="nav-links"> ... </ul>

3) Replace ONLY the <li> menu items with the contents of:
   templates/snippets/mpe_nav_items.html
   - This removes Distribution.
   - Leaves your existing Get A Quote button exactly as-is.

4) Dropdown styling:
   If your CSS already supports dropdowns, you can skip this.
   Otherwise:
   - Copy static/mpe_nav_dropdowns.css into your static folder.
   - Add this line in your base template <head> AFTER your main stylesheet:

     <link rel="stylesheet" href="{% static 'mpe_nav_dropdowns.css' %}">

5) Restart:
   python manage.py runserver
   Then Ctrl+F5 refresh.

Notes:
- Links are direct paths to avoid NoReverseMatch issues.
- If you want role-based hiding (only show Admin for staff/superusers), tell me and I’ll provide a conditional snippet.
