"""
services/export.py

Exports the page-level rollup (with verdicts) to CSV, JSON, or
Markdown. This is the deliberate substitute for baking AI analysis
into the app — TrafficOps produces clean structured data, and
analysis happens externally (EAI Workstation, or Claude directly)
where the judgment and the model choice stay in Jaren's control.
"""

import csv
import json
from pathlib import Path


def _rows_to_dicts(rollup_rows) -> list[dict]:
    """Convert sqlite3.Row objects into plain dicts for export."""
    return [dict(row) for row in rollup_rows]


def export_csv(rollup_rows, output_path: Path) -> Path:
    """
    Write page rollup data to CSV.

    @param rollup_rows  list[sqlite3.Row]  From database.pages.fetch_page_rollup
    @param output_path  Path  Where to write the file
    @return Path  The path written to
    """
    data = _rows_to_dicts(rollup_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        if not data:
            f.write("")
            return output_path
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    return output_path


def export_json(rollup_rows, output_path: Path) -> Path:
    """
    Write page rollup data to JSON — the most direct format for
    handing off to an AI model for analysis.

    @param rollup_rows  list[sqlite3.Row]  From database.pages.fetch_page_rollup
    @param output_path  Path  Where to write the file
    @return Path  The path written to
    """
    data = _rows_to_dicts(rollup_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return output_path


def export_markdown(rollup_rows, output_path: Path, site_label: str = "") -> Path:
    """
    Write page rollup data as a Markdown table — readable directly,
    or pasteable into a Claude/AI Workstation conversation without
    needing a file upload.

    @param rollup_rows  list[sqlite3.Row]  From database.pages.fetch_page_rollup
    @param output_path  Path  Where to write the file
    @param site_label   str   Optional site name for the heading
    @return Path  The path written to
    """
    data = _rows_to_dicts(rollup_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [f"# TrafficOps Export — {site_label}\n"] if site_label else ["# TrafficOps Export\n"]

    if data:
        headers = list(data[0].keys())
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in data:
            lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
