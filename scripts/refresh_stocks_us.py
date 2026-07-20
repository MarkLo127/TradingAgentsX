#!/usr/bin/env python3
"""
Refresh frontend/public/data/stocks-us.json against SEC EDGAR's ticker
registry, so newly-listed US tickers show up in autocomplete / the results
page company name (see scripts/refresh_stocks_tw.py for the TW-market
sibling of this script and the full rationale).

SEC EDGAR's company_tickers.json (https://www.sec.gov/files/company_tickers.json)
is, near-certainly, the original source of stocks-us.json: its row order
(NVDA, AAPL, GOOGL, MSFT, AMZN, ...) and company-name casing line up almost
exactly with Python's str.title() applied to SEC's ALL-CAPS "title" field
("MICROSOFT CORP" -> "Microsoft Corp", "BERKSHIRE HATHAWAY INC" -> "Berkshire
Hathaway Inc", etc. -- both verified against the existing file). A handful of
existing rows don't match that transform exactly (e.g. LLY kept as "ELI LILLY
& Co"), so the file was evidently spot-edited by hand afterward -- this
script only appends brand-new tickers, it never rewrites existing rows.

Note: SEC's feed only includes tickers that file with the SEC. It won't
include foreign issuers trading OTC under a Rule 12g3-2(b) exemption (many of
the "...F"-suffixed pink-sheet ADRs already in the file), so tickers present
in the JSON but absent from this feed are NOT necessarily delisted -- don't
use this script to prune the file.

Usage:
    python scripts/refresh_stocks_us.py [contact_email]

    contact_email overrides the User-Agent contact SEC's fair-access policy
    asks automated clients to declare (https://www.sec.gov/os/webmaster-faq#developers).
    Defaults to a placeholder -- pass your own email when running this for real.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

from _json_rows import write_rows

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
DATA_PATH = Path(__file__).resolve().parent.parent / "frontend" / "public" / "data" / "stocks-us.json"
DEFAULT_CONTACT = "TradingAgentsX-maintainer example@example.com"


def fetch_sec_tickers(contact: str) -> list[dict]:
    req = Request(SEC_TICKERS_URL, headers={"User-Agent": contact})
    with urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return list(data.values())


def main() -> None:
    contact = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONTACT
    if contact == DEFAULT_CONTACT:
        print(f"Using placeholder User-Agent contact ({contact}); pass a real "
              f"email as an argument to be a good API citizen: "
              f"python scripts/refresh_stocks_us.py you@example.com\n")

    existing_rows: list[list[str]] = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    existing_tickers = {row[0] for row in existing_rows}

    sec_rows = fetch_sec_tickers(contact)

    new_rows = [
        [r["ticker"], r["title"].title()]
        for r in sec_rows
        if r.get("ticker") and r["ticker"] not in existing_tickers
    ]
    # Dedupe (SEC lists one row per CIK, so a company with multiple share
    # classes/CIKs could in theory repeat a ticker) while preserving order.
    seen: set[str] = set()
    deduped_new_rows = []
    for row in new_rows:
        if row[0] in seen:
            continue
        seen.add(row[0])
        deduped_new_rows.append(row)

    if deduped_new_rows:
        print(f"Adding {len(deduped_new_rows)} newly-registered ticker(s):")
        for row in deduped_new_rows:
            print(f"  {row[0]}  {row[1]}")
        updated_rows = existing_rows + deduped_new_rows
        write_rows(DATA_PATH, updated_rows)
        print(f"\nWrote {len(updated_rows)} total rows to {DATA_PATH}")
    else:
        print("No new tickers found -- data file already covers every SEC-registered ticker.")


if __name__ == "__main__":
    main()
