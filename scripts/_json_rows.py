"""Shared writer for the flat-array-of-rows JSON data files under
frontend/public/data/ (stocks-tw.json, stocks-us.json).

These files are committed and hand-read in diffs, so they're formatted one
row per line rather than json.dumps(..., indent=2)'s default of exploding
every nested array element onto its own line -- using indent=2 directly
would rewrite every existing row's formatting and bury the real diff (a
handful of appended tickers) under tens of thousands of unrelated line
changes.
"""
from __future__ import annotations

import json
from pathlib import Path


def write_rows(path: Path, rows: list[list[str]]) -> None:
    lines = ["["]
    for i, row in enumerate(rows):
        suffix = "," if i < len(rows) - 1 else ""
        lines.append("  " + json.dumps(row, ensure_ascii=False) + suffix)
    lines.append("]")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
