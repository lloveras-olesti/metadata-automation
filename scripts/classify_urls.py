#!/usr/bin/env python3
"""
Script 1: classify_urls.py
Reads all in-scope Screaming Frog CSVs, classifies URLs, joins with category lookups,
and produces the central working file: data/master_urls.csv.

Expected input files in data/screaming-frog/ (standard Screaming Frog export names):
    page_titles_missing.csv
    page_titles_below_30_characters.csv
    page_titles_over_60_characters.csv
    meta_description_missing.csv
    meta_description_below_70_characters.csv
    meta_description_over_155_characters.csv

Language detection and URL classification use patterns defined in utils.py,
which reads its configuration from config.yaml.

Usage:
    python scripts/classify_urls.py
"""

import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing dependency: pip install pandas")

BASE_DIR = Path(__file__).parent.parent
SF_DIR = BASE_DIR / "data" / "screaming-frog"
OUTPUT = BASE_DIR / "data" / "master_urls.csv"

# Mapping: filename (without .csv) → issue code
ISSUE_MAP = {
    "page_titles_missing":              "missing_title",
    "page_titles_below_30_characters":  "title_too_short",
    "page_titles_over_60_characters":   "title_too_long",
    "meta_description_missing":         "missing_meta",
    "meta_description_below_70_characters": "meta_too_short",
    "meta_description_over_155_characters": "meta_too_long",
}


def load_sf_csv(path: Path, issue: str) -> pd.DataFrame:
    """Load one Screaming Frog CSV, return normalised DataFrame."""
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str).fillna("")
    df = df.rename(columns={"Address": "url"})

    # Extract title column if present
    df["title"] = df.get("Title 1", pd.Series("", index=df.index)).fillna("")
    df["meta_description"] = df.get("Meta Description 1", pd.Series("", index=df.index)).fillna("")

    df["issue"] = issue
    return df[["url", "title", "meta_description", "issue"]]


def load_all_csvs() -> pd.DataFrame:
    frames = []
    for stem, issue in ISSUE_MAP.items():
        path = SF_DIR / f"{stem}.csv"
        if not path.exists():
            print(f"  WARNING: {path.name} not found — skipping")
            continue
        df = load_sf_csv(path, issue)
        frames.append(df)
        print(f"  Loaded {len(df):>5} rows from {path.name}")
    return pd.concat(frames, ignore_index=True)


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge rows for the same URL:
    - issues: comma-joined sorted set
    - title / meta_description: first non-empty value wins
    """
    def first_nonempty(series):
        for v in series:
            if isinstance(v, str) and v.strip():
                return v
        return ""

    agg = df.groupby("url", sort=False).agg(
        issue=("issue", lambda x: ",".join(sorted(set(x)))),
        title=("title", first_nonempty),
        meta_description=("meta_description", first_nonempty),
    ).reset_index()
    return agg


def join_lookups(df: pd.DataFrame) -> pd.DataFrame:
    """Add category_label column by joining with both lookup CSVs."""
    from utils import load_lookup, normalise_url

    languages = df["lang"].unique()
    lookups = {}
    for lang in languages:
        try:
            lookups[lang] = load_lookup(lang, BASE_DIR)
        except FileNotFoundError:
            print(f"  WARNING: lookup file for lang='{lang}' not found — category_label will be empty")
            lookups[lang] = {}

    def get_label(row) -> str:
        url_norm = normalise_url(row["url"])
        lang = row["lang"]
        return lookups.get(lang, {}).get(url_norm, {}).get("label", "")

    df["category_label"] = df.apply(get_label, axis=1)
    return df


def main():
    # Make utils importable from scripts/
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import classify_url, extract_lang

    print("Script 1: classify_urls.py")
    print(f"  Reading from: {SF_DIR.relative_to(BASE_DIR)}")
    print()

    df = load_all_csvs()
    print(f"\n  Total rows before dedup: {len(df)}")

    df = deduplicate(df)
    print(f"  Unique URLs after dedup:  {len(df)}")

    # Classify and extract language
    df["url_type"] = df["url"].apply(classify_url)
    df["lang"] = df["url"].apply(extract_lang)

    # Join lookups for category/geo labels
    df = join_lookups(df)

    # Add empty output columns
    df["new_title"] = ""
    df["new_meta"] = ""
    df["title_action"] = ""
    df["meta_action"] = ""
    df["status"] = "pending"

    # Reorder columns
    cols = [
        "url", "lang", "url_type", "issue",
        "title", "meta_description", "category_label",
        "new_title", "new_meta", "title_action", "meta_action", "status",
    ]
    df = df[cols]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"\n  Written {len(df)} rows to {OUTPUT.relative_to(BASE_DIR)}")

    # Summary by url_type and issue
    print("\n  URL type breakdown:")
    for url_type, count in df["url_type"].value_counts().items():
        print(f"    {url_type:<12} {count:>6}")

    print("\n  Issue breakdown:")
    from collections import Counter
    issue_counter: Counter = Counter()
    for issues in df["issue"]:
        for i in issues.split(","):
            issue_counter[i.strip()] += 1
    for issue, count in sorted(issue_counter.items()):
        print(f"    {issue:<40} {count:>6}")

    print("\nDone.")


if __name__ == "__main__":
    main()
