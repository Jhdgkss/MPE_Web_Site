
# PATCHED SECTION — clean PDF attachment handling

import logging
logger = logging.getLogger(__name__)

# ... (rest of your imports and code remain unchanged above)

# Find the block inside send_order_emails and replace with this:

# --- PDF attachment ---
if cfg.attach_order_pdf:
    try:
        from .pdf_utils import generate_order_pdf_bytes  # lazy import
        pdf_bytes = generate_order_pdf_bytes(order, request=request) or b""
    except Exception:
        logger.exception("Failed to generate order PDF bytes for email attachment")
        pdf_bytes = b""

# ... (rest of your function continues unchanged)
