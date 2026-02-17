from django import template
import re

register = template.Library()

_HEX_RE = re.compile(r'^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$')

def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.strip()
    m = _HEX_RE.match(hex_color)
    if not m:
        return None
    h = m.group(1)
    if len(h) == 3:
        h = ''.join([c*2 for c in h])
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r, g, b)

def _relative_luminance(rgb):
    # sRGB -> linear
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    rl, gl, bl = channel(r), channel(g), channel(b)
    return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl

@register.filter
def contrast_text(color_value, dark="#0f172a"):
    """Return white or dark text depending on background color brightness.

    Usage:
      {{ settings.hero_background_color|contrast_text }}
    Accepts hex colors like '#001a4d' or '001a4d' or short '#0af'.
    Falls back to white if parsing fails.
    """
    if not color_value:
        return "#ffffff"
    rgb = _hex_to_rgb(str(color_value))
    if rgb is None:
        return "#ffffff"
    lum = _relative_luminance(rgb)
    # Threshold tuned for UI backgrounds; tweak if needed
    return dark if lum > 0.55 else "#ffffff"
