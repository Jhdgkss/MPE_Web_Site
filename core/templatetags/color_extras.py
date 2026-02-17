from django import template

register = template.Library()


def _parse_hex(color: str):
    color = (color or '').strip()
    if not color:
        return None
    if color.startswith('#'):
        color = color[1:]
    if len(color) == 3:
        color = ''.join(ch * 2 for ch in color)
    if len(color) != 6:
        return None
    try:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        return r, g, b
    except ValueError:
        return None


def _relative_luminance(rgb):
    # WCAG relative luminance
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


@register.filter(name='contrast_text')
def contrast_text(bg_color: str, dark: str = '#0f172a') -> str:
    """Return a readable text color (white or dark) for a given hex background."""
    rgb = _parse_hex(bg_color)
    if rgb is None:
        return '#ffffff'
    lum = _relative_luminance(rgb)
    # threshold tuned for dark hero sections; adjust if needed
    return dark if lum > 0.55 else '#ffffff'
