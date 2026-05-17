#!/usr/bin/env python3
"""
Script 5: pilot_validation.py
Validates the generated values in master_urls.csv and produces a sample for human review.

Length limits are read from config.yaml → seo_limits.

Usage:
    python scripts/pilot_validation.py             # default 50-row sample
    python scripts/pilot_validation.py --sample 100
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_loader import load_config

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing dependency: pip install pandas")

BASE_DIR = Path(__file__).parent.parent
MASTER = BASE_DIR / "data" / "master_urls.csv"
SAMPLE_OUT = BASE_DIR / "data" / "pilot_sample.csv"

_cfg = load_config()
TITLE_MIN: int = _cfg["seo_limits"]["title_min"]
TITLE_MAX: int = _cfg["seo_limits"]["title_max"]
META_MIN: int = _cfg["seo_limits"]["meta_min"]
META_MAX: int = _cfg["seo_limits"]["meta_max"]


def validate_row(row) -> tuple[bool, list[str]]:
    """Return (ok, list_of_notes) for a single row."""
    notes = []

    title_action = row.get("title_action", "")
    meta_action = row.get("meta_action", "")
    new_title = str(row.get("new_title", ""))
    new_meta = str(row.get("new_meta", ""))

    # Title validation
    if new_title:
        t_len = len(new_title)
        if t_len < TITLE_MIN:
            notes.append(f"title too short ({t_len}c)")
        elif t_len > TITLE_MAX:
            notes.append(f"title too long ({t_len}c)")

    if title_action == "ai_failed":
        notes.append("AI title generation failed — manual fix needed")

    if title_action not in ("", "manual_review", "ai_failed") and not new_title:
        notes.append("title_action set but new_title is empty")

    # Meta validation
    if new_meta:
        m_len = len(new_meta)
        if m_len < META_MIN:
            notes.append(f"meta too short ({m_len}c)")
        elif m_len > META_MAX:
            notes.append(f"meta too long ({m_len}c)")

    if meta_action not in ("", "manual_review") and not new_meta:
        notes.append("meta_action set but new_meta is empty")

    # Category/geo should have a label
    url_type = row.get("url_type", "")
    if url_type in ("category", "geo") and not row.get("category_label", ""):
        notes.append("category_label missing for category/geo page")

    ok = len(notes) == 0
    return ok, notes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=50, help="Number of rows in pilot sample")
    args = parser.parse_args()

    print("Script 5: pilot_validation.py")

    df = pd.read_csv(MASTER, encoding="utf-8", dtype=str).fillna("")

    # Validate every row that has any generated value
    processed = df[(df["new_title"] != "") | (df["new_meta"] != "")].copy()
    print(f"  Rows with generated content: {len(processed)}")

    validation_ok = []
    validation_notes = []

    for _, row in processed.iterrows():
        ok, notes = validate_row(row)
        validation_ok.append(ok)
        validation_notes.append("; ".join(notes) if notes else "")

    processed["validation_ok"] = validation_ok
    processed["validation_notes"] = validation_notes

    # Report
    n_ok = sum(validation_ok)
    n_fail = len(validation_ok) - n_ok
    print(f"\n  Validation results:")
    print(f"    Pass: {n_ok}")
    print(f"    Fail: {n_fail}")

    if n_fail > 0:
        print("\n  Failed rows:")
        failed = processed[~processed["validation_ok"]]
        for _, row in failed.head(20).iterrows():
            print(f"    [{row['url_type']:8}] {row['url'][-60:]}")
            print(f"             {row['validation_notes']}")

    # Sample output
    sample = processed.head(args.sample)
    sample.to_csv(SAMPLE_OUT, index=False, encoding="utf-8")
    print(f"\n  Sample ({len(sample)} rows) written to {SAMPLE_OUT.relative_to(BASE_DIR)}")

    # Action breakdown
    print("\n  Title action breakdown:")
    for action, count in processed["title_action"].value_counts().items():
        print(f"    {action:<20} {count:>6}")

    print("\n  Meta action breakdown:")
    for action, count in processed["meta_action"].value_counts().items():
        print(f"    {action:<20} {count:>6}")

    print("\nDone.")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
