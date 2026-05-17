#!/usr/bin/env python3
"""
verify_prestashop.py — PrestaShop API key health check.

Run this before executing any pipeline script that touches the API.
It verifies authentication, read access on products/categories,
and prints the language IDs you need to set in .env.

Usage:
    python scripts/verify_prestashop.py
"""

import os
import sys

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: pip install requests")

API_KEY = os.getenv("PRESTASHOP_API_KEY", "")
BASE_URL = os.getenv("PRESTASHOP_BASE_URL", "").rstrip("/")

OK = "[ OK ]"
FAIL = "[FAIL]"


def check(label: str, url: str, session: requests.Session) -> dict | None:
    """
    Make a GET request. Print result. Return parsed JSON on success, None on failure.
    """
    try:
        r = session.get(url, timeout=10)
    except requests.exceptions.ConnectionError as e:
        print(f"  {FAIL} {label}: connection error — {e}")
        return None

    if r.status_code == 200:
        print(f"  {OK}   {label} (HTTP 200)")
        try:
            return r.json()
        except Exception:
            return {}
    else:
        print(f"  {FAIL} {label}: HTTP {r.status_code}")
        if r.status_code == 401:
            print("         → API key rejected. Check PRESTASHOP_API_KEY.")
        elif r.status_code == 403:
            print("         → Key valid but no permission for this resource.")
        return None


def main() -> int:
    print("PrestaShop API Verification")
    print(f"  Base URL : {BASE_URL or '(not set)'}")
    print(f"  API key  : {'*' * min(len(API_KEY), 6) + '...' if API_KEY else '(not set)'}")
    print()

    if not API_KEY:
        print(f"  {FAIL} PRESTASHOP_API_KEY is not set. Copy .env.example to .env and fill it in.")
        return 1
    if not BASE_URL:
        print(f"  {FAIL} PRESTASHOP_BASE_URL is not set.")
        return 1

    session = requests.Session()
    session.auth = (API_KEY, "")
    session.headers.update({"Accept": "application/json"})

    failures = 0

    # 1. API root
    data = check(
        "API root reachable",
        f"{BASE_URL}/api/?output_format=JSON",
        session,
    )
    if data is None:
        failures += 1

    # 2. Products read
    data = check(
        "Products: read access",
        f"{BASE_URL}/api/products?limit=1&output_format=JSON",
        session,
    )
    if data is None:
        failures += 1

    # 3. Categories read
    data = check(
        "Categories: read access",
        f"{BASE_URL}/api/categories?limit=1&output_format=JSON",
        session,
    )
    if data is None:
        failures += 1

    # 4. Languages — print IDs so user can set them in .env
    lang_data = check(
        "Languages: read access",
        f"{BASE_URL}/api/languages?output_format=JSON",
        session,
    )
    if lang_data is None:
        failures += 1
    else:
        try:
            langs = lang_data.get("languages", [])
            if langs:
                print()
                print("  Language IDs found (set these in .env):")
                for lang in langs:
                    lang_id = lang.get("id", "?")
                    ld = session.get(
                        f"{BASE_URL}/api/languages/{lang_id}?output_format=JSON",
                        timeout=10,
                    )
                    if ld.status_code == 200:
                        iso = ld.json().get("language", {}).get("iso_code", "?")
                        name = ld.json().get("language", {}).get("name", "?")
                        env_var = f"PRESTASHOP_LANG_ID_{iso.upper()}"
                        current = os.getenv(env_var, "(not set)")
                        status = "OK" if current == str(lang_id) else f"→ SET {env_var}={lang_id} in .env"
                        print(f"    id={lang_id}  iso_code={iso}  name={name}  {status}")
        except Exception as e:
            print(f"  Warning: could not parse language details — {e}")

    print()
    if failures == 0:
        print("  All checks passed. API is ready.")
        return 0
    else:
        print(f"  {failures} check(s) failed. Fix the issues above before running the pipeline.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
