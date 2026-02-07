from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import EmailConfiguration
from .pdf_utils import generate_order_pdf_bytes


def send_order_emails(order, request=None) -> None:
    """Send customer + internal order emails (optional PDF attachment)."""
    cfg = EmailConfiguration.get_config()

    from_email = cfg.from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None) or "sales@mpe-uk.com"
    reply_to = [cfg.reply_to_email] if cfg.reply_to_email else None
    internal_to = cfg.parsed_internal_recipients()

    # Customer email (contact email)
    contact = getattr(order, "contact", None)
    customer_email = getattr(contact, "email", "") if contact else ""

    order_ref = getattr(order, "order_number", "") or str(getattr(order, "id", ""))

    pdf_bytes = b""
    filename = f"Order_{order_ref}.pdf"
    if cfg.attach_order_pdf:
        pdf_bytes = generate_order_pdf_bytes(order, request=request) or b""

    # Render simple bodies (keep it text-only for deliverability)
    footer = cfg.footer_text or ""
    customer_subject = (cfg.customer_subject or "Your order from MPE UK Ltd (Order {order_ref})").format(order_ref=order_ref)
    internal_subject = (cfg.internal_subject or "New website order received (Order {order_ref})").format(order_ref=order_ref)

    customer_body = (
        f"Thank you for your order.\n\n"
        f"Order reference: {order_ref}\n"
        f"Status: {getattr(order, 'status', '')}\n\n"
        f"A PDF copy is attached for your records.\n\n"
        f"{footer}"
    ).strip()

    internal_body = (
        f"A new website order has been placed.\n\n"
        f"Order reference: {order_ref}\n"
        f"Customer: {getattr(contact, 'name', '') if contact else ''}\n"
        f"Company: {getattr(contact, 'company', '') if contact else ''}\n"
        f"Email: {customer_email}\n\n"
        f"A PDF copy is attached.\n\n"
        f"{footer}"
    ).strip()

    # Send customer email
    if cfg.send_to_customer and customer_email:
        msg = EmailMessage(
            subject=customer_subject,
            body=customer_body,
            from_email=from_email,
            to=[customer_email],
            reply_to=reply_to,
        )
        if pdf_bytes:
            msg.attach(filename, pdf_bytes, "application/pdf")
        msg.send(fail_silently=False)

    # Send internal email
    if cfg.send_to_internal and internal_to:
        msg2 = EmailMessage(
            subject=internal_subject,
            body=internal_body,
            from_email=from_email,
            to=internal_to,
            reply_to=reply_to,
        )
        if pdf_bytes:
            msg2.attach(filename, pdf_bytes, "application/pdf")
        msg2.send(fail_silently=False)
