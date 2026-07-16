"""
personal_profile.py

Jaren's personal-account voice, distinct from the three CAS page voices
and from EchoCast (which handles article syndication).

Two content modes:
  - "original": a standalone personal note/update, not tied to a page post
  - "share_from_page": a short personal reaction/intro when resharing
    a Break/Verify, Not Quite Sentient, or CAS page post to the personal
    account. Short, not a rewrite of the page post.
"""

PERSONAL_VOICE = (
    "Personal account, broader audience than the niche pages, acts as a funnel "
    "to the pages and the sites. Same person, less filtered, more life-in-general. "
    "Not a brand voice. Talks the way Jaren actually talks, direct, no polish for "
    "polish's sake."
)

PLATFORMS = {
    "facebook": {
        "max_length": "150-300 words, longer is fine if it earns it",
        "format_notes": "Native text post. Can carry a link, can stand alone. Paragraph breaks over hashtags.",
    },
    "instagram": {
        "max_length": "under 150 words caption",
        "format_notes": "Visual-first, caption supports the image. Light hashtag use at the end, 3-5 max, not a hashtag block.",
    },
    "threads": {
        "max_length": "under 500 characters",
        "format_notes": "Punchy, conversational, built for reply threads. No hashtags. Reads like a reply-bait opener.",
    },
    "x": {
        "max_length": "under 280 characters",
        "format_notes": "Single sharp point. No hashtag stuffing. Can be a thread starter if the note has more than one beat.",
    },
}

SHARE_FROM_PAGE_RULE = (
    "This is a short personal intro line added when resharing a page post, "
    "not a rewrite of the page post itself. One or two sentences, personal "
    "framing on why this is worth their attention, then the share carries the rest."
)
