from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic.edit import FormView

from .brevo_api import send_transactional_email

logger = logging.getLogger(__name__)


class CustomerPasswordResetRequestView(FormView):
    """Password reset request view that sends mail via Brevo HTTP API.

    - Uses Brevo (same mechanism as invoices / enquiries) for reliability.
    - Avoids account enumeration by always redirecting to "done".
    - If multiple users share an email, each user will receive a reset link.
    """

    template_name = "registration/password_reset_form.html"
    form_class = PasswordResetForm

    def form_valid(self, form: PasswordResetForm) -> HttpResponse:
        request: HttpRequest = self.request
        email = form.cleaned_data.get("email")

        # Railway / reverse proxies may terminate TLS before Django.
        protocol = "https" if request.is_secure() else "http"
        domain = request.get_host()

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "") or "sales@mpe-uk.com"
        sender_name = getattr(settings, "BREVO_SENDER_NAME", "") or "MPE UK Ltd"

        try:
            users = list(form.get_users(email))
            for user in users:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                reset_path = reverse(
                    "customer_password_reset_confirm",
                    kwargs={"uidb64": uid, "token": token},
                )
                reset_link = request.build_absolute_uri(reset_path)

                context = {
                    "email": email,
                    "user": user,
                    "domain": domain,
                    "protocol": protocol,
                    "uid": uid,
                    "token": token,
                    "reset_link": reset_link,
                    "site_name": "MPE UK Ltd",
                }

                subject = render_to_string(
                    "registration/password_reset_subject.txt", context
                ).strip()
                body = render_to_string("registration/password_reset_email.txt", context)

                send_transactional_email(
                    subject=subject,
                    text=body,
                    to_emails=[email],
                    from_email=from_email,
                    sender_name=sender_name,
                )
        except Exception:
            # Never crash the password reset page.
            logger.exception("Password reset email send failed")

        return redirect("customer_password_reset_done")
