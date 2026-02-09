from __future__ import annotations

from decimal import Decimal
from io import BytesIO
from typing import Optional, Tuple

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


def _get_pdf_config():
    # Local import to avoid startup issues during migrations
    from .models import PDFConfiguration

    return PDFConfiguration.get_config()


def _order_items_and_total(order) -> Tuple[list, Decimal]:
    items = list(getattr(order, "items", []).all()) if hasattr(order, "items") else []
    total = Decimal("0.00")
    for item in items:
        try:
            if hasattr(item, "line_total"):
                total += item.line_total()
            else:
                # Fallback if model stores a numeric total directly
                total += Decimal(str(getattr(item, "total", "0") or "0"))
        except Exception:
            continue
    return items, total


def _absolute_media_url(request, url: str) -> str:
    if not url:
        return ""
    # Cloudinary is usually already absolute
    if url.startswith("http://") or url.startswith("https://") or url.startswith("file://"):
        return url
    if request is not None:
        return request.build_absolute_uri(url)
    return url


def generate_order_pdf_bytes(order, request=None) -> bytes:
    """Generate an Order Summary PDF as bytes.

    Preferred renderer: WeasyPrint (HTML + branding + logo).
    Fallback: ReportLab (plain but reliable).
    """

    cfg = _get_pdf_config()
    items, total = _order_items_and_total(order)

    # Resolve logo
    logo_url = ""
    try:
        if cfg.pdf_logo:
            # If storage doesn't provide .path (e.g. Cloudinary), use .url
            if hasattr(cfg.pdf_logo, "path"):
                try:
                    logo_url = f"file://{cfg.pdf_logo.path}"
                except Exception:
                    logo_url = ""
            if not logo_url:
                logo_url = _absolute_media_url(request, getattr(cfg.pdf_logo, "url", "") or "")
    except Exception:
        logo_url = ""

    # -----------------------
    # Attempt 1: WeasyPrint
    # -----------------------
    try:
        import weasyprint  # type: ignore

        ctx = {
            "order": order,
            "items": items,
            "total": total,
            "pdf_cfg": cfg,
            "pdf_logo_url": logo_url,
            "generated_at": timezone.now(),
        }

        # Use app template (core/templates/core/order_pdf.html)
        html_string = render_to_string("core/order_pdf.html", ctx, request=request)

        # base_url helps WeasyPrint resolve relative URLs (if any)
        base_url = None
        if request is not None:
            base_url = request.build_absolute_uri("/")
        else:
            base_url = str(settings.BASE_DIR)

        pdf_bytes = weasyprint.HTML(string=html_string, base_url=base_url).write_pdf()
        return pdf_bytes or b""

    except Exception as e:
        logger.warning("PDF: WeasyPrint failed, falling back to ReportLab. err=%s", e)

    # -----------------------
    # Attempt 2: ReportLab
    # -----------------------
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        x_margin = 18 * mm
        y = height - 18 * mm

        # Header bar (accent)
        try:
            from reportlab.lib import colors

            accent = getattr(cfg, "accent_color", "#2E7D32") or "#2E7D32"
            c.setFillColor(colors.HexColor(accent))
            c.rect(0, height - 20 * mm, width, 20 * mm, fill=1, stroke=0)
        except Exception:
            pass

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_margin, height - 14 * mm, getattr(cfg, "document_title", "Order Summary") or "Order Summary")

        # Logo (best-effort)
        c.setFillColorRGB(0, 0, 0)
        if cfg.pdf_logo and hasattr(cfg.pdf_logo, "path"):
            try:
                c.drawImage(cfg.pdf_logo.path, width - 55 * mm, height - 18 * mm, width=40 * mm, height=14 * mm, mask='auto')
            except Exception:
                pass

        y -= 30 * mm
        c.setFont("Helvetica", 10)
        c.drawString(x_margin, y, f"Order: #{getattr(order, 'order_number', '') or getattr(order, 'id', '')}")
        y -= 6 * mm
        c.drawString(x_margin, y, f"Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}")

        y -= 12 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_margin, y, "Items")
        y -= 7 * mm
        c.setFont("Helvetica", 9)

        for item in items[:35]:
            name = getattr(item, "product_name", None) or getattr(getattr(item, "product", None), "name", "") or "Item"
            qty = getattr(item, "quantity", 1)
            line_total = ""
            try:
                if hasattr(item, "line_total"):
                    line_total = f"{item.line_total():.2f}"
            except Exception:
                line_total = ""
            c.drawString(x_margin, y, f"{qty} x {name}")
            if line_total:
                c.drawRightString(width - x_margin, y, line_total)
            y -= 5.5 * mm
            if y < 25 * mm:
                c.showPage()
                y = height - 25 * mm
                c.setFont("Helvetica", 9)

        y -= 6 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(width - x_margin, y, f"Total: {total:.2f}")

        if getattr(cfg, "show_page_numbers", True):
            c.setFont("Helvetica", 8)
            c.drawRightString(width - x_margin, 10 * mm, "Page 1")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.read()

    except Exception:
        logger.exception("PDF: ReportLab fallback failed.")
        return b""
