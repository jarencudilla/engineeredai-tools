"""
card_styles.py

Visual tokens per page. Edit colors here, never in svg_card.py.
Placeholder colors flagged below — swap for confirmed site tokens.
"""

CARD_STYLES = {
    "break_verify": {
        "bg": "#1E3A5F",       # placeholder — steel blue, QA/testing feel
        "text": "#F5F5F5",
        "accent": "#4FA8D8",
        "label": "BREAK/VERIFY",
    },
    "not_quite_sentient": {
        "bg": "#2D1B4E",       # EAI purple family (confirmed direction)
        "text": "#F5F5F5",
        "accent": "#A78BFA",
        "label": "NOT QUITE SENTIENT",
    },
    "cas": {
        "bg": "#7C2D12",       # placeholder — CAS network color not yet confirmed
        "text": "#F5F5F5",
        "accent": "#F97316",
        "label": "CTRL+ALT+SURVIVE",
    },
    "personal": {
        "bg": "#111111",       # placeholder — neutral, distinct from all pages
        "text": "#F5F5F5",
        "accent": "#E5E5E5",
        "label": None,          # no page label on personal cards
    },
}

CARD_WIDTH = 1080
CARD_HEIGHT = 1080  # square, safe default across FB/IG/Threads feed crops
