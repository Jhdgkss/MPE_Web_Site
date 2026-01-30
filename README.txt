Hero carousel dots at bottom of hero banner (desktop)

Copy the file into your project, overwriting the existing one:
- static/styles.css

Why this fixes it
- Previously the hero section vertically centered its content (align-items:center), so the carousel height collapsed to the content height. The dots are positioned 'bottom: ...' relative to the carousel, so they appeared mid-banner.
- This patch changes the hero flex alignment to stretch so the hero__content and hero-carousel can occupy the full hero height.
- The carousel is already position:relative; the dots remain position:absolute; bottom: ...; so now 'bottom' really means the bottom of the hero banner.

Note
- On small screens (<980px) your CSS intentionally switches the dots to 'position: static' below the content. If you want them pinned to the bottom on mobile as well, tell me and I’ll adjust that media query.
