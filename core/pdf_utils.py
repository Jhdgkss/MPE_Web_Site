
# PATCHED pdf_utils.py

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from .models import SiteConfiguration

styles = getSampleStyleSheet()


def generate_order_pdf_bytes(order):
    site_config = SiteConfiguration.objects.first()
    hide_prices = getattr(site_config, "hide_shop_prices", False)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    elements = []
    elements.append(Paragraph(f"Order #{order.id}", styles["Title"]))
    elements.append(Spacer(1, 12))

    # table header
    if hide_prices:
        data = [["Item", "Qty"]]
    else:
        data = [["Item", "Qty", "Price", "Line Total"]]

    total = 0

    for item in order.items.all():
        price = getattr(item, "unit_price_gbp", 0) or 0
        line_total = price * item.quantity

        if not hide_prices:
            total += line_total

        if hide_prices:
            row = [item.product.name, item.quantity]
        else:
            price_display = "On request" if price == 0 else f"£{price:.2f}"
            line_display = "—" if price == 0 else f"£{line_total:.2f}"
            row = [item.product.name, item.quantity, price_display, line_display]

        data.append(row)

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
    ]))

    elements.append(table)

    if not hide_prices:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Total: £{total:.2f}", styles["Heading2"]))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
