"""
TMview India Trademark Scraper
================================
Features:
  - Calls TMview's internal JSON API directly (no HTML parsing)
  - Pagination with automatic checkpoint saving (resume if interrupted)
  - Date range filtering to handle large datasets in chunks
  - Rate limiting (polite delays between requests)
  - Saves output as JSON + CSV + Excel
  - Retry logic on network errors

Requirements:
  pip install requests pandas openpyxl

Usage:
  python tmview_india_scraper.py

  # Or with date range (recommended for large pulls):
  python tmview_india_scraper.py --from-date 2020-01-01 --to-date 2024-12-31

  # Resume an interrupted run:
  python tmview_india_scraper.py --resume
"""

import requests
import json
import time
import csv
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("[WARNING] pandas not installed. Excel/CSV output will use built-in csv module.")
    print("          Run: pip install pandas openpyxl")

# ─── Configuration ────────────────────────────────────────────────────────────

API_URL = "https://www.tmdn.org/tmview/api/trademark/search"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.tmdn.org/tmview/",
    "Origin": "https://www.tmdn.org",
}

PAGE_SIZE = 100          # Max records per request (TMview supports up to 100)
SLEEP_BETWEEN_PAGES = 1  # Seconds to wait between requests
MAX_RETRIES = 5          # Retries on network error
CHECKPOINT_EVERY = 10    # Save checkpoint every N pages
OUTPUT_DIR = Path("tmview_output")

# ─── Argument Parser ──────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(description="Scrape TMview India trademark data")
    parser.add_argument("--from-date", default=None,
                        help="Filter from date (YYYY-MM-DD). Example: 2020-01-01")
    parser.add_argument("--to-date", default=None,
                        help="Filter to date (YYYY-MM-DD). Example: 2024-12-31")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from the last checkpoint")
    parser.add_argument("--max-records", type=int, default=None,
                        help="Stop after N records (useful for testing)")
    parser.add_argument("--output", default="india_trademarks",
                        help="Output filename prefix (default: india_trademarks)")
    return parser.parse_args()

# ─── API Call ────────────────────────────────────────────────────────────────

def build_payload(page, from_date=None, to_date=None):
    payload = {
        "page": page,
        "pageSize": PAGE_SIZE,
        "criteria": "C",
        "offices": ["IN"],
        "territories": ["IN"],
        "sortColumn": "applicationDate",
        "desc": True,
    }
    if from_date:
        payload["applicationDateFrom"] = from_date
    if to_date:
        payload["applicationDateTo"] = to_date
    return payload


def fetch_page(page, from_date=None, to_date=None):
    payload = build_payload(page, from_date, to_date)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                API_URL,
                json=payload,
                headers=HEADERS,
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            print(f"  [HTTP Error] {e} — attempt {attempt}/{MAX_RETRIES}")
            if resp.status_code in (429, 503):
                wait = 10 * attempt
                print(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            elif attempt == MAX_RETRIES:
                raise
        except requests.exceptions.RequestException as e:
            print(f"  [Network Error] {e} — attempt {attempt}/{MAX_RETRIES}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(5 * attempt)
    return None

# ─── Checkpoint ───────────────────────────────────────────────────────────────

def load_checkpoint(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"page": 1, "records": []}


def save_checkpoint(path, page, records):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump({"page": page, "records": records}, f)
    tmp.replace(path)  # Atomic write

# ─── Flatten a trademark record ───────────────────────────────────────────────

def flatten_record(tm):
    """Flatten nested trademark dict to a single-level dict for CSV/Excel."""
    flat = {}
    simple_keys = [
        "applicationNumber", "trademarkName", "trademarkStatus",
        "applicationDate", "registrationDate", "expiryDate",
        "office", "trademarkType", "kind", "niceClasses",
        "goodsAndServices", "applicantName", "applicantAddress",
        "trademarkImageUrl", "st13",
    ]
    for key in simple_keys:
        val = tm.get(key, "")
        if isinstance(val, list):
            val = "; ".join(str(v) for v in val)
        flat[key] = val

    # Nested: applicants
    applicants = tm.get("applicants", [])
    if applicants:
        flat["applicantName"] = "; ".join(
            a.get("name", "") for a in applicants if a.get("name")
        )
        flat["applicantAddress"] = "; ".join(
            a.get("address", "") for a in applicants if a.get("address")
        )

    # Nested: Nice classes
    nice = tm.get("niceClasses", [])
    if isinstance(nice, list):
        flat["niceClasses"] = "; ".join(str(n) for n in nice)

    return flat

# ─── Save outputs ─────────────────────────────────────────────────────────────

def save_json(records, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"  ✓ JSON saved → {path}")


def save_csv(records, path):
    if not records:
        return
    flat = [flatten_record(r) for r in records]
    keys = list(flat[0].keys())
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    print(f"  ✓ CSV saved → {path}")


def save_excel(records, path):
    if not HAS_PANDAS:
        print("  [SKIP] Excel output requires pandas. Run: pip install pandas openpyxl")
        return
    if not records:
        return
    flat = [flatten_record(r) for r in records]
    df = pd.DataFrame(flat)

    # Friendly column names
    rename = {
        "applicationNumber": "Application No.",
        "trademarkName": "Trademark Name",
        "trademarkStatus": "Status",
        "applicationDate": "Application Date",
        "registrationDate": "Registration Date",
        "expiryDate": "Expiry Date",
        "office": "Office",
        "trademarkType": "Type",
        "kind": "Kind",
        "niceClasses": "Nice Classes",
        "goodsAndServices": "Goods & Services",
        "applicantName": "Applicant Name",
        "applicantAddress": "Applicant Address",
        "trademarkImageUrl": "Image URL",
        "st13": "ST13",
    }
    df.rename(columns=rename, inplace=True)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Trademarks")
        ws = writer.sheets["Trademarks"]

        # Auto-fit column widths
        for col in ws.columns:
            max_len = max(
                (len(str(cell.value)) if cell.value else 0 for cell in col), default=10
            )
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)

    print(f"  ✓ Excel saved → {path}")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    OUTPUT_DIR.mkdir(exist_ok=True)

    checkpoint_path = OUTPUT_DIR / f"{args.output}_checkpoint.json"
    out_json  = OUTPUT_DIR / f"{args.output}.json"
    out_csv   = OUTPUT_DIR / f"{args.output}.csv"
    out_excel = OUTPUT_DIR / f"{args.output}.xlsx"

    # Load checkpoint or start fresh
    if args.resume and checkpoint_path.exists():
        state = load_checkpoint(checkpoint_path)
        start_page = state["page"]
        all_records = state["records"]
        print(f"[RESUME] Resuming from page {start_page} ({len(all_records)} records already collected)")
    else:
        start_page = 1
        all_records = []

    print(f"\n{'='*55}")
    print(f"  TMview India Trademark Scraper")
    print(f"  Date range : {args.from_date or 'all'} → {args.to_date or 'all'}")
    print(f"  Page size  : {PAGE_SIZE} records/page")
    print(f"  Output dir : {OUTPUT_DIR.resolve()}")
    print(f"{'='*55}\n")

    # First request to get total count
    print(f"[INFO] Fetching page 1 to get total record count...")
    first_page = fetch_page(1, args.from_date, args.to_date)
    if not first_page:
        print("[ERROR] Could not reach TMview API. Check your internet connection.")
        return

    # TMview may return total under different keys — check both
    total = (
        first_page.get("total")
        or first_page.get("totalElements")
        or first_page.get("count")
        or "?"
    )
    print(f"[INFO] Total records available: {total}")
    if args.max_records:
        print(f"[INFO] Will stop after {args.max_records} records (--max-records flag)")

    # Add first page results if starting fresh
    if start_page == 1:
        trademarks = first_page.get("trademarks") or first_page.get("results") or []
        all_records.extend(trademarks)
        start_page = 2

    # Paginate
    page = start_page
    while True:
        if args.max_records and len(all_records) >= args.max_records:
            print(f"\n[STOP] Reached --max-records limit ({args.max_records})")
            break

        print(f"  Fetching page {page}... ", end="", flush=True)
        data = fetch_page(page, args.from_date, args.to_date)

        if not data:
            print("No response — stopping.")
            break

        trademarks = data.get("trademarks") or data.get("results") or []
        if not trademarks:
            print("No more records.")
            break

        all_records.extend(trademarks)
        print(f"{len(trademarks)} records fetched (total so far: {len(all_records)})")

        # Checkpoint
        if page % CHECKPOINT_EVERY == 0:
            save_checkpoint(checkpoint_path, page + 1, all_records)
            print(f"  [Checkpoint saved at page {page}]")

        # Check if we've got everything
        if isinstance(total, int) and len(all_records) >= total:
            print(f"\n[DONE] Collected all {total} records.")
            break

        page += 1
        time.sleep(SLEEP_BETWEEN_PAGES)

    # Save final outputs
    print(f"\n[SAVING] {len(all_records)} records...")
    save_json(all_records, out_json)
    save_csv(all_records, out_csv)
    save_excel(all_records, out_excel)

    # Clean up checkpoint
    if checkpoint_path.exists():
        checkpoint_path.unlink()
        print("  ✓ Checkpoint file removed")

    print(f"\n[COMPLETE] All done! Files saved in: {OUTPUT_DIR.resolve()}\n")


if __name__ == "__main__":
    main()