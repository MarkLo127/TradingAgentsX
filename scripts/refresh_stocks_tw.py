#!/usr/bin/env python3
"""
Refresh frontend/public/data/stocks-tw.json against the official TWSE/TPEx
listed-company registries, so newly-IPO'd tickers get picked up.

The autocomplete/name-lookup dataset used by the frontend
(frontend/lib/stock-search.ts) is a static, hand-curated JSON snapshot. It
never restricts which ticker can be *analyzed* -- the ticker input is free
text and the backend fetches real data for anything -- but a ticker that
IPO'd after the snapshot was taken won't get autocomplete suggestions or a
resolved company name on the results page (falls back to showing the raw
ticker code).

This script does NOT try to rebuild the file from scratch (that would throw
away the curated full English legal names, e.g. "Taiwan Semiconductor
Manufacturing Co., Ltd." for 2330, which the official feeds don't provide --
they only have short English abbreviations like "TSMC"). Instead it:

  1. Pulls the current full listed-company registry from TWSE + TPEx.
  2. Diffs it against the existing JSON by stock_id.
  3. Appends any stock_id present live but missing from the JSON, using the
     official Chinese short name and English abbreviation as a placeholder.
  4. Leaves every existing row untouched (order matters: row index doubles
     as a popularity rank in stock-search.ts).

Note: the TWSE/TPEx feeds used here (t187ap03_L / mopsfin_t187ap03_O) only
cover ordinary listed companies -- not ETFs, warrants, bonds, or 興櫃
(emerging board) securities. Don't use this script's output to infer that
something *not* in the live registry has been delisted; it may just be a
security type these feeds don't carry.

Run it every so often (e.g. after a batch of new listings) -- there's no
cron wired up for this on purpose, since new IPOs are infrequent (order of
tens per year) and a silent auto-write into a committed data file is the
kind of change a human should skim before it lands.

Usage:
    python scripts/refresh_stocks_tw.py
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _json_rows import write_rows

TWSE_LISTED_URL = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
TPEX_LISTED_URL = "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O"

DATA_PATH = Path(__file__).resolve().parent.parent / "frontend" / "public" / "data" / "stocks-tw.json"


def fetch_json(url: str) -> list[dict]:
    # tpex.org.tw's certificate is missing a Subject Key Identifier extension,
    # which Python's ssl module (OpenSSL 3.x) rejects outright even though
    # the chain itself is valid -- curl's TLS stack accepts it. Shell out to
    # curl (still doing real certificate verification, no -k/--insecure)
    # rather than disabling verification in requests.
    result = subprocess.run(
        ["curl", "-sS", "--fail", "--max-time", "30", url],
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def load_live_registry() -> dict[str, tuple[str, str, str]]:
    """stock_id -> (zh_name, en_abbr, market)"""
    registry: dict[str, tuple[str, str, str]] = {}

    for row in fetch_json(TWSE_LISTED_URL):
        stock_id = row.get("公司代號", "").strip()
        if not stock_id:
            continue
        registry[stock_id] = (
            row.get("公司簡稱", "").strip(),
            row.get("英文簡稱", "").strip(),
            "twse",
        )

    for row in fetch_json(TPEX_LISTED_URL):
        stock_id = row.get("SecuritiesCompanyCode", "").strip()
        if not stock_id:
            continue
        registry[stock_id] = (
            row.get("CompanyAbbreviation", "").strip(),
            row.get("Symbol", "").strip(),
            "tpex",
        )

    return registry


def main() -> None:
    existing_rows: list[list[str]] = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    existing_ids = {row[0] for row in existing_rows}

    # Trailing non-ticker rows (sector/index entries with alpha ids like
    # "TAIEX") must stay last -- new tickers get spliced in before them.
    split_at = len(existing_rows)
    while split_at > 0 and not existing_rows[split_at - 1][0].isdigit():
        split_at -= 1
    ticker_rows, tail_rows = existing_rows[:split_at], existing_rows[split_at:]

    live_registry = load_live_registry()

    new_rows = [
        [stock_id, zh_name, en_abbr, market]
        for stock_id, (zh_name, en_abbr, market) in live_registry.items()
        if stock_id not in existing_ids
    ]
    new_rows.sort(key=lambda r: r[0])

    if new_rows:
        print(f"Adding {len(new_rows)} newly-listed ticker(s):")
        for row in new_rows:
            print(f"  {row[0]}  {row[1]}  ({row[2] or 'no English name'})  [{row[3]}]")
    else:
        print("No new tickers found -- data file already covers every currently-listed company.")

    if new_rows:
        updated_rows = ticker_rows + new_rows + tail_rows
        write_rows(DATA_PATH, updated_rows)
        print(f"\nWrote {len(updated_rows)} total rows to {DATA_PATH}")


if __name__ == "__main__":
    main()
