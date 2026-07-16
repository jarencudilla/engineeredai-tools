"""
daily_run.py

CLI entry point. Reads today_notes.json, runs the shared cycle, prints
where the output landed. All actual logic lives in cycle_runner.py so
the browser UI (app.py) uses the exact same code path.

    python daily_run.py
"""

import json
from pathlib import Path

from cycle_runner import run_cycle

NOTES_PATH = Path(__file__).parent / "today_notes.json"


def run():
    with open(NOTES_PATH, "r", encoding="utf-8") as f:
        notes = json.load(f)

    results = run_cycle(notes)
    print(f"Done. Markdown written to {results['_markdown_path']}")
    for key, data in results.items():
        if key.startswith("_"):
            continue
        print(f"  {key}: {data['svg_path']}")


if __name__ == "__main__":
    run()
