NAVBAR PATCH v2 – FIX NoReverseMatch

Problem:
- Your project does not have a URL name called 'home', so `{% url 'home' %}` crashes.

Fix:
- This patch switches the navbar to DIRECT PATH LINKS:
  /, /machines/, /tooling/, /customer/documents/, /customer/dashboard/, /staff/login/, /admin/login/, /admin/site-editing/, /quote/

Apply:
- Copy templates/base.html into your project's templates folder (merge the <nav> block if needed)
- Restart server

Note:
- If your login URL isn't /accounts/login/, change that one link to your real login page.
