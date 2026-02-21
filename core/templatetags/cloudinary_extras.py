from __future__ import annotations

from django import template

register = template.Library()


@register.filter(name="cloudinary_raw_pdf")
def cloudinary_raw_pdf(url: str | None) -> str:
    """Best-effort fix for Cloudinary PDF URLs generated via MediaCloudinaryStorage.

    Some Cloudinary setups return 401 or fail for PDFs when delivered via /image/upload/.
    If the URL looks like a Cloudinary URL and ends with .pdf (or contains typical PDF paths),
    switch to /raw/upload/ which is the correct resource type for non-images.

    If the URL isn't a Cloudinary URL, or doesn't look like a PDF, return as-is.
    """
    if not url:
        return ""

    u = str(url)

    # If it's already a raw URL, leave it.
    if "/raw/upload/" in u:
        return u

    # Heuristics: treat as PDF if it ends with .pdf or is in your known upload folders
    is_pdf = u.lower().endswith(".pdf") or "/spec_sheets/" in u.lower() or "/machines/documents/" in u.lower()

    if is_pdf and "/image/upload/" in u and "res.cloudinary.com/" in u:
        return u.replace("/image/upload/", "/raw/upload/")

    return u
