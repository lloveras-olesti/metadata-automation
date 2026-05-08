#!/usr/bin/env python3
"""
Script 6: write_to_prestashop.py
Writes validated title and meta description changes to PrestaShop via Webservice API.

Defaults to --dry-run mode. Use --live to actually write to production.

Requires environment variables (set in .env):
    PRESTASHOP_API_KEY
    PRESTASHOP_BASE_URL
    PRESTASHOP_LANG_ID_{LANG}   (one per configured language, e.g. PRESTASHOP_LANG_ID_ES=1)

NOTE: This script is specific to the PrestaShop Webservice (XML-based API with Basic Auth).
For other CMS platforms, implement an equivalent connector script.

Usage:
    python scripts/write_to_prestashop.py --dry-run   # safe preview (default)
    python scripts/write_to_prestashop.py --live       # write to production
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
LOG_OK = BASE_DIR / "data" / "write_log.csv"
LOG_ERR = BASE_DIR / "data" / "write_errors.csv"

API_KEY = os.getenv("PRESTASHOP_API_KEY", "")
BASE_URL = os.getenv("PRESTASHOP_BASE_URL", "").rstrip("/")
LANG_ID_ES = int(os.getenv("PRESTASHOP_LANG_ID_ES", "1"))
LANG_ID_CA = int(os.getenv("PRESTASHOP_LANG_ID_CA", "2"))


def get_xml(session: requests.Session, url: str) -> etree._Element | None:
    """Fetch a PrestaShop resource as XML. Returns the root element or None."""
    try:
        r = session.get(url, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"    GET error: {e}")
        return None
    if r.status_code != 200:
        print(f"    GET HTTP {r.status_code}: {url}")
        return None
    try:
        return etree.fromstring(r.content)
    except Exception as e:
        print(f"    XML parse error: {e}")
        return None


def set_language_field(root: etree._Element, field_name: str, lang_id: int, value: str) -> bool:
    """
    Update a language-specific field in the XML.
    Returns True if the field was found and updated.
    """
    matches = root.xpath(f"//{field_name}/language[@id='{lang_id}']")
    if not matches:
        field_els = root.xpath(f"//{field_name}")
        if not field_els:
            return False
        lang_el = etree.SubElement(field_els[0], "language")
        lang_el.set("id", str(lang_id))
        matches = [lang_el]

    matches[0].text = value
    return True


def put_xml(session: requests.Session, url: str, root: etree._Element) -> tuple[bool, str]:
    """PUT the modified XML back to PrestaShop. Returns (success, message)."""
    xml_bytes = etree.tostring(root, encoding="utf-8", xml_declaration=True)
    try:
        r = session.put(
            url,
            data=xml_bytes,
            headers={"Content-Type": "text/xml; charset=utf-8"},
            timeout=20,
        )
    except requests.exceptions.RequestException as e:
        return False, str(e)

    if r.status_code in (200, 201):
        return True, f"HTTP {r.status_code}"
    return False, f"HTTP {r.status_code}: {r.text[:200]}"


def process_product(
    session: requests.Session,
    product_id: int,
    lang_id: int,
    new_title: str,
    new_meta: str,
    dry_run: bool,
) -> tuple[bool, str]:
    url = f"{BASE_URL}/api/products/{product_id}"
    root = get_xml(session, url)
    if root is None:
        return False, "GET failed"

    changed = False
    if new_title:
        ok = set_language_field(root, "meta_title", lang_id, new_title)
        if not ok:
            return False, "meta_title field not found in XML"
        changed = True
    if new_meta:
        ok = set_language_field(root, "meta_description", lang_id, new_meta)
        if not ok:
            return False, "meta_description field not found in XML"
        changed = True

    if not changed:
        return True, "nothing to write"

    if dry_run:
        return True, f"DRY-RUN: would PUT meta_title={new_title[:40]!r} meta_desc={new_meta[:40]!r}"

    return put_xml(session, url, root)


def lookup_cms_id(session: requests.Session, base_url: str, slug: str) -> int | None:
    """Look up a CMS page ID by its link_rewrite slug. Returns None if not found."""
    url = f"{base_url}/api/cms?filter[link_rewrite]={slug}&display=[id,link_rewrite]&output_format=JSON"
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("cms", [])
            if pages:
                return int(pages[0]["id"])
    except Exception:
        pass
    return None


def process_cms(
    session: requests.Session,
    cms_id: int,
    lang_id: int,
    new_title: str,
    new_meta: str,
    dry_run: bool,
) -> tuple[bool, str]:
    url = f"{BASE_URL}/api/cms/{cms_id}"
    root = get_xml(session, url)
    if root is None:
        return False, "GET failed"

    changed = False
    if new_title:
        ok = set_language_field(root, "meta_title", lang_id, new_title)
        if not ok:
            return False, "meta_title field not found in XML"
        changed = True
    if new_meta:
        ok = set_language_field(root, "meta_description", lang_id, new_meta)
        if not ok:
            return False, "meta_description field not found in XML"
        changed = True

    if not changed:
        return True, "nothing to write"

    if dry_run:
        return True, f"DRY-RUN: would PUT meta_title={new_title[:40]!r} meta_desc={new_meta[:40]!r}"

    return put_xml(session, url, root)


def process_category(
    session: requests.Session,
    category_id: int,
    lang_id: int,
    new_title: str,
    new_meta: str,
    dry_run: bool,
) -> tuple[bool, str]:
    url = f"{BASE_URL}/api/categories/{category_id}"
    root = get_xml(session, url)
    if root is None:
        return False, "GET failed"

    changed = False
    if new_title:
        set_language_field(root, "meta_title", lang_id, new_title)
        changed = True
    if new_meta:
        set_language_field(root, "meta_description", lang_id, new_meta)
        changed = True

    if not changed:
        return True, "nothing to write"

    if dry_run:
        return True, f"DRY-RUN: would PUT meta_title={new_title[:40]!r} meta_desc={new_meta[:40]!r}"

    return put_xml(session, url, root)


def main():
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import extract_product_id, extract_category_id, extract_cms_id, extract_url_slug, LANGUAGES

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default)")
    group.add_argument("--live", action="store_true", help="Actually write to PrestaShop")
    args = parser.parse_args()

    dry_run = not args.live

    if not API_KEY:
        sys.exit("PRESTASHOP_API_KEY not set.")
    if not BASE_URL:
        sys.exit("PRESTASHOP_BASE_URL not set.")

    # Build lang_id map from env vars
    lang_id_map = {}
    for lang in LANGUAGES:
        val = os.getenv(f"PRESTASHOP_LANG_ID_{lang.upper()}")
        if val:
            lang_id_map[lang] = int(val)
    # Fallback for backwards compatibility
    if not lang_id_map:
        lang_id_map = {"es": LANG_ID_ES, "ca": LANG_ID_CA}

    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"Script 6: write_to_prestashop.py  [{mode}]")
    if dry_run:
        print("  Pass --live to actually write to production.")
    print()

    df = pd.read_csv(MASTER, encoding="utf-8", dtype=str).fillna("")

    # Only rows with content to write and pending status
    mask = (
        ((df["new_title"] != "") | (df["new_meta"] != ""))
        & (df["status"] == "pending")
    )
    targets = df[mask]
    print(f"  Rows to process: {len(targets)}")

    session = requests.Session()
    session.auth = (API_KEY, "")

    log_ok = []
    log_err = []

    for idx, row in targets.iterrows():
        url_type = row["url_type"]
        lang = row["lang"]
        url = row["url"]
        new_title = row["new_title"]
        new_meta = row["new_meta"]
        lang_id = lang_id_map.get(lang, list(lang_id_map.values())[0])

        if url_type == "geo":
            log_err.append({
                "url": url,
                "url_type": url_type,
                "error": "geo_endpoint_unknown — manual action required",
            })
            df.at[idx, "status"] = "write_skipped_geo"
            continue

        if url_type == "product":
            rid = extract_product_id(url)
            if rid is None:
                log_err.append({"url": url, "url_type": url_type, "error": "cannot extract product ID"})
                continue
            success, msg = process_product(session, rid, lang_id, new_title, new_meta, dry_run)

        elif url_type == "category":
            rid = extract_category_id(url)
            if rid is None:
                log_err.append({"url": url, "url_type": url_type, "error": "cannot extract category ID"})
                continue
            success, msg = process_category(session, rid, lang_id, new_title, new_meta, dry_run)

        elif url_type == "cms":
            cms_id = extract_cms_id(url)
            if cms_id is None:
                slug = extract_url_slug(url)
                cms_id = lookup_cms_id(session, BASE_URL, slug)
            if cms_id is None:
                log_err.append({"url": url, "url_type": url_type, "error": "cannot resolve CMS ID"})
                continue
            success, msg = process_cms(session, cms_id, lang_id, new_title, new_meta, dry_run)

        else:
            log_err.append({"url": url, "url_type": url_type, "error": f"unhandled type: {url_type}"})
            continue

        if success:
            log_ok.append({"url": url, "url_type": url_type, "result": msg})
            if not dry_run:
                df.at[idx, "status"] = "written"
            print(f"  OK  [{url_type}] {url[-60:]}")
        else:
            log_err.append({"url": url, "url_type": url_type, "error": msg})
            if not dry_run:
                df.at[idx, "status"] = "write_error"
            print(f"  ERR [{url_type}] {url[-60:]}: {msg}")

        time.sleep(0.15)

    # Save logs
    pd.DataFrame(log_ok).to_csv(LOG_OK, index=False, encoding="utf-8")
    pd.DataFrame(log_err).to_csv(LOG_ERR, index=False, encoding="utf-8")
    if not dry_run:
        df.to_csv(MASTER, index=False, encoding="utf-8")

    print(f"\n  Written OK:  {len(log_ok)}")
    print(f"  Errors/skip: {len(log_err)}")
    print(f"  Log: {LOG_OK.relative_to(BASE_DIR)}")
    print(f"  Errors: {LOG_ERR.relative_to(BASE_DIR)}")
    print("\nDone.")


if __name__ == "__main__":
    main()
