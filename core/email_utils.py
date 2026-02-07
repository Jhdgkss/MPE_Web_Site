from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMessage

from .models import EmailConfiguration
from .pdf_utils import generate_order_pdf_bytes


def send_order_emails(order, request=None) -> None:
    """Send customer + internal order emails (optional PDF attachment).

    Uses EmailConfiguration singleton (editable in Django admin).
    """

    cfg = EmailConfiguration.get_config()

    from_email = cfg.from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None) or "sales@mpe-uk.com"
    reply_to = [cfg.reply_to_email] if cfg.reply_to_email else None
    internal_to = cfg.parsed_internal_recipients()

    contact = getattr(order, "contact", None)
    customer_email = getattr(contact, "email", "") if contact else ""

    order_id = getattr(order, "id", "")
    order_number = getattr(order, "order_number", "")
    order_ref = order_number or str(order_id)

    # Optional PDF attachment
    pdf_bytes = b""
    filename = (cfg.pdf_filename_template or "Order_{order_id}.pdf").format(
        order_id=order_id, order_number=order_number or order_id
    )

    if cfg.attach_order_pdf:
        try:
            pdf_bytes = generate_order_pdf_bytes(order, request=request) or b""
        except Exception:
            # Don't block email sending if PDF generation fails
            pdf_bytes = b""

    footer = (cfg.footer_note or "").strip()

    customer_subject = (cfg.customer_subject_template or "Your order from MPE UK Ltd (Ref {order_ref})").format(
        order_ref=order_ref,
        order_id=order_id,
        order_number=order_number,
    )

    internal_subject = (cfg.internal_subject_template or "New website order received (Ref {order_ref})").format(
        order_ref=order_ref,
        order_id=order_id,
        order_number=order_number,
    )

    # Bodies (text-only for deliverability)
    customer_lines = [
        "Thank you for your order.",
        "",
        f"Order reference: {order_ref}",
        f"Status: {getattr(order, 'status', '')}",
    ]
    if pdf_bytes:
        customer_lines += ["", "A PDF copy is attached for your records."]
    if footer:
        customer_lines += ["", footer]
    customer_body = "\n".join(customer_lines).strip()

    internal_lines = [
        "A new website order has been placed.",
        "",
        f"Order reference: {order_ref}",
        f"Customer: {getattr(contact, 'name', '') if contact else ''}",
        f"Company: {getattr(contact, 'company', '') if contact else ''}",
        f"Email: {customer_email}",
        f"Phone: {getattr(contact, 'phone', '') if contact else ''}",
    ]
    if pdf_bytes:
        internal_lines += ["", "A PDF copy is attached."]
    if footer:
        internal_lines += ["", footer]
    internal_body = "\n".join(internal_lines).strip()

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
