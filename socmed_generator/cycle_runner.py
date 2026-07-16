"""
cycle_runner.py

Single responsibility: given a notes dict, run the full generation cycle
(page posts + personal posts + SVG cards), write files, return results
for display. Used by both daily_run.py (CLI) and app.py (browser UI).
"""

from datetime import date
from pathlib import Path

from rotation_tracker import get_next_slot
from generator import generate_page_post, generate_personal_post
from svg_card import generate_card_svg
from voice_profiles import PAGES

OUTPUT_DIR = Path(__file__).parent / "outputs"


def _find_usable_slot(page_key: str, raw_note: str) -> tuple[str, dict]:
    """
    Advances rotation until it lands on a slot that can actually run today:
    either a no-fact slot (always usable) or a fact slot with a real note.
    Bounded to the number of slots on the page so it can't loop forever.
    """
    slots = PAGES[page_key]["slots"]
    for _ in range(len(slots)):
        slot_key = get_next_slot(page_key)
        slot = slots[slot_key]
        if not slot["needs_fact"] or raw_note:
            return slot_key, slot
    # every slot needs a fact and none was given — fall back to whatever's current
    return slot_key, slot


def run_cycle(notes: dict) -> dict:
    """
    Runs the full generation cycle. Writes markdown + SVG files to outputs/.
    Returns a dict of results for display: {page_key/platform: {text, svg_path}}
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()
    results = {}
    output_lines = [f"# Social Posts — {today}\n"]

    active_pages = notes.get("active_pages", ["break_verify", "not_quite_sentient", "cas"])

    for page_key in active_pages:
        raw_note = notes.get(page_key, "").strip()
        slot_key, slot = _find_usable_slot(page_key, raw_note)

        post = generate_page_post(page_key, slot_key, raw_note)
        output_lines.append(f"## {page_key} — {slot_key}\n\n{post}\n")

        svg_path = OUTPUT_DIR / f"{page_key}_{today}.svg"
        svg_path.write_text(generate_card_svg(page_key, post), encoding="utf-8")

        results[page_key] = {"slot": slot_key, "text": post, "svg_path": str(svg_path)}

    personal = notes.get("personal")
    if personal and personal.get("note", "").strip():
        posts = generate_personal_post(
            mode=personal.get("mode", "original"),
            raw_note=personal["note"],
            platforms=personal.get("platforms", ["facebook", "instagram", "threads"]),
        )
        output_lines.append("## Personal\n")
        for platform, post in posts.items():
            output_lines.append(f"### {platform}\n\n{post}\n")

            svg_path = OUTPUT_DIR / f"personal_{platform}_{today}.svg"
            svg_path.write_text(generate_card_svg("personal", post), encoding="utf-8")

            results[f"personal_{platform}"] = {"text": post, "svg_path": str(svg_path)}

    md_path = OUTPUT_DIR / f"social_{today}.md"
    md_path.write_text("\n".join(output_lines), encoding="utf-8")
    results["_markdown_path"] = str(md_path)

    return results
