from __future__ import annotations

import logging

from django.conf import settings
from django.utils import timezone

from .brevo_api import BrevoAttachment, send_transactional_email
from .models import EmailConfiguration
from .pdf_utils import generate_order_pdf_bytes

logger = logging.getLogger(__name__)


def _sender_name() -> str:
    # Optional env override, then Django setting, then default.
    return (
        getattr(settings, "BREVO_SENDER_NAME", None)
        or getattr(settings, "SITE_NAME", None)
        or "MPE UK Ltd"
    )


def send_quote_request_emails(
    *,
    name: str,
    email: str,
    company: str = "",
    phone: str = "",
    product: str = "",
    output: str = "",
    message: str = "",
    machine: str = "",
) -> None:
    """Send a 'Get a Quote' enquiry email to internal recipients + optional customer acknowledgement."""

    cfg = EmailConfiguration.get_config()

    from_email = cfg.from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None) or "sales@mpe-uk.com"
    internal_to = cfg.parsed_internal_recipients()

    # Make it easy for sales to reply directly to the enquirer
    reply_to = email or (cfg.reply_to_email or "")

    subject = "Website quote request"
    if company:
        subject += f" - {company}"
    if name:
        subject += f" ({name})"

    lines = [
        "A new quote request has been submitted via the website.",
        "",
        f"Name: {name}",
        f"Company: {company}",
        f"Email: {email}",
        f"Phone: {phone}",
    ]
    if machine:
        lines += [f"Machine/page: {machine}"]
    if product:
        lines += [f"What are you packing?: {product}"]
    if output:
        lines += [f"Required output: {output}"]
    if message:
        lines += ["", "Message:", message]

    footer = (cfg.footer_note or "").strip()
    if footer:
        lines += ["", footer]

    body = "\n".join([ln for ln in lines if ln is not None]).strip()

    if not internal_to:
        raise RuntimeError("No internal email recipients configured.")

    logger.info("QUOTE_EMAIL: attempting internal send to=%s", ",".join(internal_to))
    send_transactional_email(
        subject=subject,
        text=body,
        to_emails=internal_to,
        from_email=from_email,
        sender_name=_sender_name(),
        reply_to=reply_to or None,
    )
    logger.info("QUOTE_EMAIL: sent internal")

    # Optional customer acknowledgement (uses cfg.send_to_customer)
    if cfg.send_to_customer and email:
        ack_subject = "Thanks — we have received your quote request"
        ack_lines = [
            f"Hi {name or 'there'},",
            "",
            "Thank you for contacting MPE UK Ltd.",
            "We have received your quote request and will get back to you as soon as possible.",
        ]
        if footer:
            ack_lines += ["", footer]
        ack_body = "\n".join(ack_lines).strip()

        logger.info("QUOTE_EMAIL: attempting customer ack to=%s", email)
        send_transactional_email(
            subject=ack_subject,
            text=ack_body,
            to_emails=[email],
            from_email=from_email,
            sender_name=_sender_name(),
            reply_to=(cfg.reply_to_email or None),
        )
        logger.info("QUOTE_EMAIL: sent customer ack to=%s", email)


def send_order_emails(order, request=None) -> None:
    """Send customer + internal order emails (optional PDF attachment).

    Uses EmailConfiguration singleton (editable in Django admin).
    """

    cfg = EmailConfiguration.get_config()

    from_email = cfg.from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None) or "sales@mpe-uk.com"
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

    # Attachments
    attachments = []
    if pdf_bytes:
        attachments = [BrevoAttachment(filename=filename, content_bytes=pdf_bytes, mime_type="application/pdf")]

    customer_ok = False
    internal_ok = False
    last_error = ""

    if cfg.send_to_customer and customer_email:
        try:
            logger.info("ORDER_EMAIL: attempting customer send order_id=%s to=%s", order_id, customer_email)
            send_transactional_email(
                subject=customer_subject,
                text=customer_body,
                to_emails=[customer_email],
                from_email=from_email,
                sender_name=_sender_name(),
                reply_to=(cfg.reply_to_email or None),
                attachments=attachments,
            )
            customer_ok = True
            logger.info("ORDER_EMAIL: sent customer order_id=%s to=%s", order_id, customer_email)
        except Exception as e:
            last_error = f"Customer email failed: {e}"
            logger.exception("ORDER_EMAIL: FAILED customer order_id=%s to=%s", order_id, customer_email)

    if cfg.send_to_internal and internal_to:
        try:
            logger.info("ORDER_EMAIL: attempting internal send order_id=%s to=%s", order_id, ",".join(internal_to))
            send_transactional_email(
                subject=internal_subject,
                text=internal_body,
                to_emails=internal_to,
                from_email=from_email,
                sender_name=_sender_name(),
                reply_to=(cfg.reply_to_email or None),
                attachments=attachments,
            )
            internal_ok = True
            logger.info("ORDER_EMAIL: sent internal order_id=%s to=%s", order_id, ",".join(internal_to))
        except Exception as e:
            prefix = "" if not last_error else last_error + " | "
            last_error = prefix + f"Internal email failed: {e}"
            logger.exception("ORDER_EMAIL: FAILED internal order_id=%s", order_id)

    # Persist status onto the order
    try:
        if hasattr(order, "email_sent_to_customer"):
            order.email_sent_to_customer = bool(customer_ok)
            order.email_sent_to_internal = bool(internal_ok)
            order.email_sent_at = timezone.now() if (customer_ok or internal_ok) else None
            order.email_last_error = last_error
            order.save(update_fields=[
                "email_sent_to_customer",
                "email_sent_to_internal",
                "email_sent_at",
                "email_last_error",
            ])
    except Exception:
        logger.exception("ORDER_EMAIL: failed to persist email status order_id=%s", order_id)

    # Do not raise here; order completion should not break if email fails.
    # Errors are stored on the order and logged.
    return
