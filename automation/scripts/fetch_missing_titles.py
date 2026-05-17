#!/usr/bin/env python3
"""
Script 2: fetch_missing_titles.py
Fetches product titles from the PrestaShop API for rows where title is empty.

Requires environment variables (set in .env):
    PRESTASHOP_API_KEY
    PRESTASHOP_BASE_URL
    PRESTASHOP_LANG_ID_ES   (or equivalent for your configured languages)
    PRESTASHOP_LANG_ID_CA

Run verify_prestashop.py first to confirm API access and discover language IDs.

Usage:
    python scripts/fetch_missing_titles.py           # full run
    python scripts/fetch_missing_titles.py --pilot   # first 10 rows only
"""

import argparse
import os
import sys
import time
from pathlib import Path

try:
    import pandas as pd
    import requests
    from lxml import etree
except ImportError:
    sys.exit("Missing dependencies: pip install pandas requests lxml")

BASE_DIR = Path(__file__).parent.parent
MASTER = BASE_DIR / "data" / "master_urls.csv"

API_KEY = os.getenv("PRESTASHOP_API_KEY", "")
BASE_URL = os.getenv("PRESTASHOP_BASE_URL", "").rstrip("/")
LANG_ID_ES = int(os.getenv("PRESTASHOP_LANG_ID_ES", "1"))
LANG_ID_CA = int(os.getenv("PRESTASHOP_LANG_ID_CA", "2"))


def get_product_name(session: requests.Session, product_id: int, lang_id: int) -> str | None:
    """
    Fetch product name from PrestaShop Webservice (XML).
    Returns the name string or None on error.
    """
    url = f"{BASE_URL}/api/products/{product_id}"
    try:
        r = session.get(url, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"    ERROR fetching product {product_id}: {e}")
        return None

    if r.status_code == 404:
        return "__404__"
    if r.status_code != 200:
        print(f"    ERROR: HTTP {r.status_code} for product {product_id}")
        return None

    try:
        root = etree.fromstring(r.content)
        # XPath: find <name><language id="{lang_id}">
        matches = root.xpath(f"//name/language[@id='{lang_id}']")
        if matches:
            return (matches[0].text or "").strip()
        # Fallback: try any language
        any_lang = root.xpath("//name/language")
        if any_lang:
            return (any_lang[0].text or "").strip()
    except Exception as e:
        print(f"    ERROR parsing XML for product {product_id}: {e}")

    return None


def main():
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import extract_product_id, LANGUAGES

    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true", help="Process only the first 10 missing rows")
    args = parser.parse_args()

    if not API_KEY:
        sys.exit("PRESTASHOP_API_KEY not set. Run verify_prestashop.py first.")
    if not BASE_URL:
        sys.exit("PRESTASHOP_BASE_URL not set.")

    # Build lang_id map from env vars: PRESTASHOP_LANG_ID_{LANG.upper()}
    lang_id_map = {}
    for lang in LANGUAGES:
        env_key = f"PRESTASHOP_LANG_ID_{lang.upper()}"
        val = os.getenv(env_key)
        if val:
            lang_id_map[lang] = int(val)
    # Fallback to ES/CA defaults for backwards compatibility
    if not lang_id_map:
        lang_id_map = {"es": LANG_ID_ES, "ca": LANG_ID_CA}

    print("Script 2: fetch_missing_titles.py")
    if args.pilot:
        print("  MODE: pilot (first 10 rows)")
    print(f"  Language ID map: {lang_id_map}")
    print()

    df = pd.read_csv(MASTER, encoding="utf-8", dtype=str).fillna("")

    # Rows that need a title fetched: title is empty and url_type is product
    mask = (df["title"] == "") & (df["url_type"] == "product") & (df["status"] == "pending")
    targets = df[mask].copy()

    if args.pilot:
        targets = targets.head(10)

    print(f"  Rows to process: {len(targets)}")
    if len(targets) == 0:
        print("  Nothing to do.")
        return

    session = requests.Session()
    session.auth = (API_KEY, "")

    ok = error = not_found = 0

    for idx, row in targets.iterrows():
        product_id = extract_product_id(row["url"])
        if product_id is None:
            print(f"  SKIP: cannot extract ID from {row['url']}")
            df.at[idx, "status"] = "title_fetch_error"
            error += 1
            continue

        lang = row["lang"]
        lang_id = lang_id_map.get(lang, list(lang_id_map.values())[0])

        name = get_product_name(session, product_id, lang_id)

        if name == "__404__":
            df.at[idx, "status"] = "title_fetch_404"
            not_found += 1
            print(f"  404: product {product_id} ({row['url'][-50:]})")
        elif name is None:
            df.at[idx, "status"] = "title_fetch_error"
            error += 1
        else:
            df.at[idx, "title"] = name
            ok += 1

        time.sleep(0.1)

    df.to_csv(MASTER, index=False, encoding="utf-8")

    print(f"\n  Results: {ok} fetched, {not_found} not found (404), {error} errors")
    print(f"  Written to {MASTER.relative_to(BASE_DIR)}")
    print("\nDone.")


if __name__ == "__main__":
    main()
