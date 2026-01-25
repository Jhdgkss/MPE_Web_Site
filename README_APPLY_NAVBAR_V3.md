MPE Navbar Patch v3 (Targeted) — KEEP EXISTING STYLING

What happened:
- The v1/v2 patch overwrote templates/base.html.
- Your original base.html contains the top contact strip, logo, layout wrappers, and CSS class hooks.
- Overwriting it removed that markup, so the menu became unstyled plain links.

Fix approach (recommended):
- RESTORE your original templates/base.html (from git / backup).
- Then apply ONLY the menu-item changes inside the existing navbar <ul>/<div> — do NOT replace the whole file.

How to restore:
1) If you use git:
   - git checkout -- templates/base.html
   (or use GitHub Desktop to discard changes to base.html)
2) If you have a copy of the old base.html, put it back.

Then apply the changes below:

A) Remove 'Distribution' menu item.
B) Add 'Customer' dropdown with:
   - Documents -> /customer/documents/
   - Metrics Dashboard -> /customer/dashboard/
C) Change 'Staff' link to point to /staff/login/ (or keep /staff/ if you prefer).
D) Add 'Admin' dropdown with:
   - Staff login -> /staff/login/
   - AdminLogin -> /admin/login/
   - Web site editing -> /admin/site-editing/

Where to edit:
- Search in base.html for the list of menu links (often <ul class="nav-links"> ... </ul>)
- Replace ONLY the <li> items for Distribution/Staff with the block in `templates/snippets/nav_items_replacement.html`.

Optional:
- If your CSS doesn’t already support dropdowns, add the CSS in `static/navbar_dropdowns.css`
  and include it next to your existing styles.css.

Notes:
- Links are direct paths to avoid NoReverseMatch issues.
- If you want role-based hiding/showing (customer vs staff vs admin), tell me and I'll
  generate the conditional Django template version that matches your user model/groups.
