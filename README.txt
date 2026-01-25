
PATCH: Main site styling restoration (SAFE)

WHAT THIS FIXES:
- Restores global site styling (navbar, layout, fonts, colours)
- Ensures styles.css is ALWAYS loaded
- Keeps dashboard.css isolated to dashboard pages only

HOW TO APPLY:
1) Copy templates/base.html over your existing base.html
2) DO NOT touch static/styles.css
3) Restart Django

WHY THIS WORKS:
Your site lost styling because styles.css was no longer being loaded.
This patch makes that impossible.

Railway-safe. No migrations. No backend changes.
