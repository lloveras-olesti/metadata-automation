#!/usr/bin/env python3
"""
purge_url_pattern.py — Remove rows matching a URL pattern from all pipeline CSVs.

Deletes every row where the URL column contains EXCLUDE_PATTERN.
Operates on all CSVs under data/ (screaming-frog inputs, master_urls, pilot_sample).
Safe to re-run: idempotent (rows already removed stay removed).

Usage:
    python scripts/purge_url_pattern.py
    python scripts/purge_url_pattern.py --pattern /blog/
    python scripts/purge_url_pattern.py --pattern /outlet/ --dry-run

Options:
    --pattern PATTERN   URL substring to exclude (default: EXCLUDE_PATTERN constant below)
    --dry-run           Report what would be removed without modifying any file
"""

import argparse
import sys
from pathlib import Path

# ── Configurable pattern ──────────────────────────────────────────────────────
EXCLUDE_PATTERN = "/blog/"
# Change this string (or pass --pattern) to target a different URL segment.
# Re-running the script after changing it will purge any newly matching rows.
# ─────────────────────────────────────────────────────────────────────────────

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing dependency: pip install pandas")

BASE_DIR = Path(__file__).parent.parent

# CSV files to process and the column name that holds the URL in each one.
# Key: glob pattern relative to BASE_DIR  |  Value: URL column name
CSV_TARGETS = {
    "data/screaming-frog/*.csv": "Address",
    "data/master_urls.csv": "url",
    "data/pilot_sample.csv": "url",
}


def process_file(path: Path, url_col: str, pattern: str, dry_run: bool) -> int:
    """
    Remove rows where url_col contains pattern.
    Returns the number of rows removed. Writes in-place unless dry_run=True.
    """
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
    except Exception as e:
        print(f"  [SKIP] {path.relative_to(BASE_DIR)}: could not read — {e}")
        return 0

    if url_col not in df.columns:
        return 0

    mask_keep = ~df[url_col].str.contains(pattern, regex=False)
    removed = int((~mask_keep).sum())

    if removed == 0:
        return 0

    if not dry_run:
        df[mask_keep].to_csv(path, index=False, encoding="utf-8")

    return removed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove rows matching a URL pattern from all pipeline CSVs."
    )
    parser.add_argument(
        "--pattern",
        default=EXCLUDE_PATTERN,
        help=f"URL substring to exclude (default: {EXCLUDE_PATTERN!r})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be removed without modifying any file",
    )
    args = parser.parse_args()

    pattern = args.pattern
    dry_run = args.dry_run

    label = "[DRY RUN] " if dry_run else ""
    print(f"{label}purge_url_pattern.py")
    print(f"  Pattern : {pattern!r}")
    print()

    total_removed = 0
    total_files_affected = 0

    for glob_pattern, url_col in CSV_TARGETS.items():
        paths = sorted(BASE_DIR.glob(glob_pattern))
        for path in paths:
            removed = process_file(path, url_col, pattern, dry_run)
            if removed > 0:
                action = "would remove" if dry_run else "removed"
                print(f"  {action:12s}  {removed:>5} rows  ← {path.relative_to(BASE_DIR)}")
                total_removed += removed
                total_files_affected += 1

    print()
    if total_removed == 0:
        print(f"  No rows matched {pattern!r} — nothing to do.")
    else:
        verb = "Would be removed" if dry_run else "Removed"
        print(f"  {verb}: {total_removed} rows across {total_files_affected} file(s).")

    if dry_run:
        print("  (Dry run — no files were modified. Remove --dry-run to apply.)")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
