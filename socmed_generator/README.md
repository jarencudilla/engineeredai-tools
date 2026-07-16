# CAS Social Generator

Offline social copy generator. Talks to local Ollama only, no external API,
no dependency on any hosted AI service.

## Setup

```
pip install -r requirements.txt
```

Open `generator.py` and set `MODEL` (line ~17) to whatever model you have
pulled in Ollama, e.g. `ollama pull llama3.1` then `MODEL = "llama3.1"`.

Ollama must be running locally (`ollama serve`) before using either mode below.

## Two ways to run

### Browser UI (recommended)

```
python app.py
```

Open http://localhost:5050. Fill in today's notes per page (leave any
field blank to skip it), hit Generate. Results show inline with card
previews. Files are written to `outputs/` automatically.

### CLI

Edit `today_notes.json` with today's raw notes, then:

```
python daily_run.py
```

Same output, written to `outputs/`, no browser needed.

## What gets generated

- One post per page (Break/Verify, Not Quite Sentient, CAS) — rotation
  slot advances automatically each run via `rotation_tracker.py` / `rotation.db`
- Personal account variants (Facebook, Instagram, Threads) if a personal
  note is provided
- One branded SVG quote-card per post, templated (not model-generated,
  small local models produce unreliable raw SVG)

## File map

| File | Responsibility |
|---|---|
| `voice_profiles.py` | Page voices + rotation slot definitions (edit tone here) |
| `personal_profile.py` | Personal voice + per-platform format rules |
| `card_styles.py` | SVG card colors/layout tokens per page (edit colors here) |
| `generator.py` | Calls Ollama, builds prompts, specialist-role engagement framing |
| `svg_card.py` | Deterministic SVG card templating |
| `rotation_tracker.py` | SQLite rotation state per page |
| `cycle_runner.py` | Shared logic — runs the full cycle, used by both CLI and UI |
| `daily_run.py` | CLI entry point |
| `app.py` | Browser UI entry point |
| `today_notes.json` | CLI input template |

## Known placeholders to fix

- `card_styles.py` — Break/Verify and CAS background colors are guesses,
  not confirmed brand hex values. Swap them if real tokens exist.
- `svg_card.py` — text wrapping is character-count based, not true font
  metrics. Approximate, not pixel-precise.

## Not included

- No connection to EAI Workstation (mentioned as a "like," not a requirement — can be wired in later if wanted)
- No posting automation — output is copy + cards for manual review and posting
- No SVG-to-MP4 conversion (separate, not needed per current scope)
