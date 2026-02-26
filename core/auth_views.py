"""Authentication-related views (customer portal password reset, etc.).

We keep these separate from core/views.py to avoid making that file even larger.
"""

from __future__ import annotations

import logging

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


class SafePasswordResetView(PasswordResetView):
    """Password reset view that never hard-crashes the page on email send failures.

    In production, SMTP/API credentials can be misconfigured temporarily.
    The standard Django view raises the exception which becomes a 500.
    We still redirect to the "done" page (standard security practice also avoids
    account enumeration).
    """

    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.txt"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as exc:  # pragma: no cover
            logger.exception("Password reset email send failed: %s", exc)
            return HttpResponseRedirect(self.get_success_url())


class SafePasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class SafePasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class SafePasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
