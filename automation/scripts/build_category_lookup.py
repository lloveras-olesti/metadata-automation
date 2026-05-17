#!/usr/bin/env python3
"""
Script 0: build_category_lookup.py
Parses the site menu HTML files and produces URL → hierarchical label lookups.

Input:  data/menus/menu_{lang}.html  (one file per language configured in config.yaml)
Output: data/lookups/category_lookup_{lang}.csv  (one file per language)

Columns:
    url    - full or relative URL as found in the menu
    label  - hierarchical label, e.g. "Literatura Catalana Poesía"
    type   - "category" or "geo"
    lang   - language code (e.g. "es", "ca")

Menu element IDs are read from config.yaml → menu.category_menu_id / menu.geo_menu_id.
Inspect the client site's HTML to find the correct values before running.

No external dependencies beyond beautifulsoup4.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_loader import load_config

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Missing dependency: pip install beautifulsoup4")

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MENUS_DIR = DATA_DIR / "menus"
OUTPUT_DIR = DATA_DIR / "lookups"

_cfg = load_config()
_menu_cfg = _cfg["menu"]
_client_cfg = _cfg["client"]

LANGUAGES: list = _client_cfg["languages"]
CATEGORY_MENU_ID: str = _menu_cfg["category_menu_id"]
GEO_MENU_ID: str | None = _menu_cfg.get("geo_menu_id")
CATEGORY_ROOT_SKIP: list = _menu_cfg.get("category_root_skip_patterns", [])


def title_case(text: str) -> str:
    """
    Convert ALL-CAPS menu label to Title Case.
    Handles special characters like Catalan middle dot correctly.
    """
    text = text.strip().lower()
    words = text.split()
    result = []
    for word in words:
        if word:
            result.append(word[0].upper() + word[1:])
    return " ".join(result)


def _is_root_link(url: str) -> bool:
    """Return True if the URL matches any of the root catalog skip patterns."""
    return any(pattern in url for pattern in CATEGORY_ROOT_SKIP)


def parse_catalog_menu(ul_element, parent_labels=None):
    """
    Recursively walk the catalog <ul>, yielding (url, hierarchical_label) tuples.
    Skips the top-level root link (e.g. "Catálogo completo").
    """
    if parent_labels is None:
        parent_labels = []

    for li in ul_element.find_all("li", recursive=False):
        a = li.find("a", recursive=False)
        if not a:
            continue

        url = a.get("href", "").strip()
        raw_text = a.get_text(strip=True)

        # Skip the catalog root link (configured via category_root_skip_patterns)
        if _is_root_link(url):
            continue

        label = title_case(raw_text)
        current_labels = parent_labels + [label]

        # Avoid redundant prefix: "Literatura Literatura De Mujeres" → "Literatura De Mujeres"
        if parent_labels and label.lower().startswith(parent_labels[-1].lower()):
            hierarchical_label = " ".join(parent_labels[:-1] + [label])
        else:
            hierarchical_label = " ".join(current_labels)

        yield url, hierarchical_label

        # Recurse into sub-menus
        sub_ul = li.find("ul", recursive=False)
        if sub_ul:
            yield from parse_catalog_menu(sub_ul, current_labels)


def parse_geo_menu(ul_element):
    """
    Parse the geo <ul>, yielding (url, label) tuples.
    Label is the plain place name as written in the menu.
    """
    for li in ul_element.find_all("li", recursive=False):
        a = li.find("a", recursive=False)
        if not a:
            continue
        url = a.get("href", "").strip()
        label = a.get_text(strip=True)
        yield url, label


def build_lookup(html_path: Path, lang: str) -> list[dict]:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    entries = []

    catalog_ul = soup.find("ul", id=CATEGORY_MENU_ID)
    if catalog_ul:
        for url, label in parse_catalog_menu(catalog_ul):
            entries.append({"url": url, "label": label, "type": "category", "lang": lang})
    else:
        print(f"  WARNING: #{CATEGORY_MENU_ID} not found in {html_path.name}", file=sys.stderr)

    if GEO_MENU_ID:
        geo_ul = soup.find("ul", id=GEO_MENU_ID)
        if geo_ul:
            for url, label in parse_geo_menu(geo_ul):
                entries.append({"url": url, "label": label, "type": "geo", "lang": lang})
        else:
            print(f"  WARNING: #{GEO_MENU_ID} not found in {html_path.name}", file=sys.stderr)

    return entries


def write_csv(entries: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "label", "type", "lang"])
        writer.writeheader()
        writer.writerows(entries)
    print(f"  Written {len(entries):>4} entries to {output_path.relative_to(BASE_DIR)}")


def main():
    print("Script 0: build_category_lookup.py")
    print(f"  Reading from: {MENUS_DIR.relative_to(BASE_DIR)}")
    print(f"  Writing to:   {OUTPUT_DIR.relative_to(BASE_DIR)}")
    print(f"  Category menu ID: #{CATEGORY_MENU_ID}")
    if GEO_MENU_ID:
        print(f"  Geo menu ID:      #{GEO_MENU_ID}")
    print()

    for lang in LANGUAGES:
        html_path = MENUS_DIR / f"menu_{lang}.html"
        if not html_path.exists():
            print(f"  ERROR: Missing input file {html_path}", file=sys.stderr)
            continue

        entries = build_lookup(html_path, lang)
        out_path = OUTPUT_DIR / f"category_lookup_{lang}.csv"
        write_csv(entries, out_path)

    print("\nDone.")


if __name__ == "__main__":
    main()
