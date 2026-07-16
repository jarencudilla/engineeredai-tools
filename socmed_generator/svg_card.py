"""
svg_card.py

Generates a branded quote-card SVG from a post's hook line.
Deterministic template, not model-generated — small local models produce
unreliable raw SVG markup, so layout is fixed Python string building instead.
"""

import textwrap
from card_styles import CARD_STYLES, CARD_WIDTH, CARD_HEIGHT

FONT_SIZE = 56
LINE_HEIGHT = 68
CHARS_PER_LINE = 26  # tuned for FONT_SIZE at CARD_WIDTH, adjust if font changes


def _wrap_text(text: str) -> list[str]:
    """Wraps text to fit the card width, returns list of lines."""
    return textwrap.wrap(text, width=CHARS_PER_LINE)


def _first_line_or_hook(post_text: str) -> str:
    """Pulls the hook — first sentence — from a generated post for the card."""
    for stop in (". ", "!\n", "?\n", ".\n"):
        if stop in post_text:
            return post_text.split(stop)[0].strip() + stop.strip()[0]
    return post_text.strip().split("\n")[0]


def generate_card_svg(page_key: str, post_text: str) -> str:
    """
    Builds an SVG quote-card for the given page/personal style using the
    post's hook line. page_key must exist in CARD_STYLES.
    """
    style = CARD_STYLES[page_key]
    hook = _first_line_or_hook(post_text)
    lines = _wrap_text(hook)

    # Vertical centering of the text block
    block_height = len(lines) * LINE_HEIGHT
    start_y = (CARD_HEIGHT - block_height) / 2 + FONT_SIZE

    text_spans = "".join(
        f'<tspan x="{CARD_WIDTH / 2}" dy="{0 if i == 0 else LINE_HEIGHT}">{line}</tspan>'
        for i, line in enumerate(lines)
    )

    label_svg = ""
    if style["label"]:
        label_svg = (
            f'<text x="60" y="{CARD_HEIGHT - 60}" font-family="monospace" '
            f'font-size="24" fill="{style["accent"]}" letter-spacing="2">{style["label"]}</text>'
        )

    svg = f'''<svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" fill="{style['bg']}"/>
  <text x="{CARD_WIDTH / 2}" y="{start_y}" text-anchor="middle" font-family="sans-serif"
        font-size="{FONT_SIZE}" font-weight="700" fill="{style['text']}">
    {text_spans}
  </text>
  {label_svg}
</svg>'''
    return svg
