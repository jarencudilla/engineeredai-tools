"""
generator.py

Offline social copy generator for EAI Workstation. Talks to local Ollama.
Two entry points:
  generate_page_post(page_key, slot_key, raw_note)   -> single post for a CAS page
  generate_personal_post(mode, raw_note, platforms)  -> dict of posts per platform

Does NOT handle article syndication — that's EchoCast's job, untouched here.
"""

import requests
from voice_profiles import PAGES
from personal_profile import PERSONAL_VOICE, PLATFORMS, SHARE_FROM_PAGE_RULE

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:12b"

# Injected into every prompt. Defines the model's job, not just its tone.
SPECIALIST_ROLE = (
    "You are acting as a social media specialist. The explicit goal of every post "
    "is to earn likes, comments, shares, and new followers, not just to state "
    "information. Every post needs:\n"
    "1. A first line that stops the scroll on its own, before any context is given.\n"
    "2. A reason for someone to comment or react, a question, a stance, an "
    "unfinished thought, something that invites a response instead of passive reading.\n"
    "3. No corporate phrasing, no hashtag stuffing, no fake urgency, no false claims "
    "of popularity or authority. Growth comes from genuine engagement, not slop tactics.\n"
    "4. The raw note provided is the only factual basis. Sharpen it, don't invent "
    "facts, testimonials, or experience that wasn't given to you."
)


def _call_ollama(prompt: str) -> str:
    """Sends a prompt to local Ollama, returns raw text response."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=600,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def generate_page_post(page_key: str, slot_key: str, raw_note: str = "") -> str:
    """
    Generates one post for a CAS page (Break/Verify, Not Quite Sentient, CAS).
    If the slot needs_fact, raw_note is required — the model shapes the real
    fact, it does not invent one. If needs_fact is False (opinion/question
    slots), the post generates from the slot description alone.
    """
    page = PAGES[page_key]
    slot = page["slots"][slot_key]

    if slot["needs_fact"] and not raw_note.strip():
        raise ValueError(
            f"Slot '{slot_key}' needs a real fact from Jaren — it claims something "
            f"specific happened. Provide raw_note or pick a different slot."
        )

    fact_block = (
        f"Raw note from the author (use only this as the factual basis, do not invent details):\n{raw_note}\n\n"
        if slot["needs_fact"]
        else "This is an opinion/question post. No specific personal event is claimed — generate from the category itself.\n\n"
    )

    prompt = (
        f"{SPECIALIST_ROLE}\n\n"
        f"Voice: {page['voice']}\n\n"
        f"Post type: {slot_key} — {slot['description']}\n\n"
        f"{fact_block}"
        f"Write one native social post in this voice, for this slot type. "
        f"No hashtags unless the voice profile calls for it."
    )
    return _call_ollama(prompt)


def generate_personal_post(mode: str, raw_note: str, platforms: list[str]) -> dict:
    """
    Generates personal-account variants across the given platforms.
    mode: "original" or "share_from_page"
    Returns {platform: post_text}
    """
    results = {}
    mode_rule = SHARE_FROM_PAGE_RULE if mode == "share_from_page" else "Standalone personal post."

    for platform in platforms:
        specs = PLATFORMS[platform]
        prompt = (
            f"{SPECIALIST_ROLE}\n\n"
            f"Voice: {PERSONAL_VOICE}\n\n"
            f"Mode: {mode_rule}\n\n"
            f"Platform: {platform}\n"
            f"Length: {specs['max_length']}\n"
            f"Format notes: {specs['format_notes']}\n\n"
            f"Raw note from the author (use only this as the factual basis, do not invent details):\n"
            f"{raw_note}\n\n"
            f"Write one post for this platform in this voice."
        )
        results[platform] = _call_ollama(prompt)

    return results
