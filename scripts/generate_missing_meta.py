#!/usr/bin/env python3
"""
Script 4: generate_missing_meta.py
Generates meta descriptions for pages with missing_meta using deterministic templates.

- product  → "{h1}{brand_suffix_long}"  (template from config.yaml)
- category → skipped — handled by generate_category_meta.py (Script 4b)
- geo      → same template as category with "Literatura de {geo_name}" as label
- cms      → skipped (manual_review)

Templates are read from config.yaml via utils.py.

Usage:
    python scripts/generate_missing_meta.py
"""

import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing dependency: pip install pandas")

BASE_DIR = Path(__file__).parent.parent
MASTER = BASE_DIR / "data" / "master_urls.csv"


def main():
    sys.path.insert(0, str(Path(__file__).parent))
    import utils

    print("Script 4: generate_missing_meta.py")

    df = pd.read_csv(MASTER, encoding="utf-8", dtype=str).fillna("")

    mask = df["issue"].str.contains("missing_meta") & (df["meta_action"] == "")
    targets = df[mask]

    print(f"  Rows to process: {len(targets)}")

    ok = 0
    skipped = 0

    for idx, row in targets.iterrows():
        url_type = row["url_type"]
        lang = row["lang"]
        label = row["category_label"]

        if url_type == "product":
            # Use original H1 (title column). Fallback to new_title if title is empty.
            h1 = row["title"] or row["new_title"]
            if not h1:
                df.at[idx, "meta_action"] = "manual_review"
                skipped += 1
                continue
            df.at[idx, "new_meta"] = utils.build_product_meta(h1, lang)
            df.at[idx, "meta_action"] = "generated"
            ok += 1

        elif url_type == "category":
            # Categories use LLM-generated metadata (Script 4b) — skipped here
            continue

        elif url_type == "geo":
            if not label:
                df.at[idx, "meta_action"] = "manual_review"
                skipped += 1
                continue
            # label for geo is the place name (e.g. "Barcelona")
            df.at[idx, "new_meta"] = utils.build_geo_meta(label, lang)
            df.at[idx, "meta_action"] = "generated"
            ok += 1

        else:
            # cms / unknown
            df.at[idx, "meta_action"] = "manual_review"
            skipped += 1

    df.to_csv(MASTER, index=False, encoding="utf-8")

    print(f"  Generated: {ok} | Skipped (manual review): {skipped}")
    print(f"  Written to {MASTER.relative_to(BASE_DIR)}")
    print("\nDone.")


if __name__ == "__main__":
    main()
