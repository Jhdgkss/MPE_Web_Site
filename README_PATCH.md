MPE Patch — Customer/Admin nav tidy-up

What this patch changes:
- Nav bar: Home | Machines | Tooling | Customer | Admin | Get a Quote
  * Customer -> /customer/ (forces customer login if not logged in)
  * Admin -> /staff/ (forces staff login if not logged in)
  * Removes Distribution and removes AdminLogin from nav.
- Adds Customer login + Customer portal landing page.
- Adds customer routes: /customer/login/ /customer/ /customer/documents/ /customer/dashboard/ /customer/logout/
  * Documents and Dashboard reuse existing templates: core/portal_documents.html and core/portal_dashboard.html
- Staff page: adds "Admin login" link (Django admin) in Quick Links.

Files included:
- templates/base.html
- core/urls.py
- core/views.py
- templates/core/customer_login.html
- templates/core/customer_portal.html
- templates/core/staff_dashboard.html

How to apply:
Unzip into your project root (same folder as manage.py), allow overwrite for the files above.
Then run:
  python manage.py runserver
