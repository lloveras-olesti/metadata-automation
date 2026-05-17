#!/usr/bin/env python3
"""
Script 3: fix_lengths.py
Fixes title and meta description length issues using deterministic rules.

- Products with title_too_long: trim by dash segments; flag as needs_ai if untrimable.
- Products with title_too_short: add brand suffix.
- Categories/geo with any title issue: rebuild from lookup label.
- meta_too_long: trim; meta_too_short: rebuild from template.

Length limits and brand suffixes are read from config.yaml via utils.py.

Note: category rows are skipped here — they get LLM-generated metadata
from generate_category_meta.py (Script 4b).

Usage:
    python scripts/fix_lengths.py
"""

import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("Missing dependency: pip install pandas")

BASE_DIR = Path(__file__).parent.parent
MASTER = BASE_DIR / "data" / "master_urls.csv"


def has_issue(issue_str: str, *codes: str) -> bool:
    issues = {i.strip() for i in issue_str.split(",") if i.strip()}
    return bool(issues & set(codes))


def fix_title(row, utils) -> tuple[str, str]:
    """
    Return (new_title, title_action).
    Only called when row has a title issue.
    """
    url_type = row["url_type"]
    lang = row["lang"]
    issue = row["issue"]
    title = row["title"]
    label = row["category_label"]

    if url_type == "product":
        if has_issue(issue, "title_too_long"):
            result = utils.build_product_title_trimmed(title, lang)
            if result is None:
                return "", "needs_ai"
            return result, "trimmed"

        if has_issue(issue, "title_too_short"):
            # Only extend if title is actually present; missing_title goes to Script 2
            if not title.strip():
                return "", "manual_review"
            return utils.build_product_title_extended(title, lang), "extended"

    if url_type in ("category", "geo"):
        if not label:
            return "", "manual_review"
        if url_type == "category":
            return utils.build_category_title(label, lang), "rebuilt"
        else:
            return utils.build_geo_title(label, lang), "rebuilt"

    # CMS or unhandled
    return "", "manual_review"


def fix_meta(row, utils) -> tuple[str, str]:
    """
    Return (new_meta, meta_action).
    Only called when row has a meta length issue (not missing — that's Script 4).
    """
    url_type = row["url_type"]
    lang = row["lang"]
    issue = row["issue"]
    meta = row["meta_description"]
    label = row["category_label"]

    if has_issue(issue, "meta_too_long"):
        trimmed = utils.trim_by_dashes(meta, utils.META_MAX)
        if trimmed:
            return trimmed, "trimmed"
        # Hard truncate
        return meta[: utils.META_MAX - 3] + "...", "truncated"

    if has_issue(issue, "meta_too_short"):
        if url_type == "product":
            # Extend with suffix
            suffix_full = utils.META_SUFFIX_FULL.get(lang, utils.META_SUFFIX_BRAND)
            candidate = meta + suffix_full
            if utils.META_MIN <= len(candidate) <= utils.META_MAX:
                return candidate, "extended"
            # Trim if over
            if len(candidate) > utils.META_MAX:
                candidate = meta + utils.META_SUFFIX_BRAND
                if len(candidate) <= utils.META_MAX:
                    return candidate, "extended"
            return candidate[:utils.META_MAX], "extended"

        if url_type in ("category", "geo") and label:
            if url_type == "category":
                return utils.build_category_meta(label, lang), "rebuilt"
            else:
                return utils.build_geo_meta(label, lang), "rebuilt"

        return "", "manual_review"

    return "", ""


def main():
    sys.path.insert(0, str(Path(__file__).parent))
    import utils

    print("Script 3: fix_lengths.py")

    df = pd.read_csv(MASTER, encoding="utf-8", dtype=str).fillna("")

    title_issues = {"title_too_long", "title_too_short", "missing_title"}
    meta_issues = {"meta_too_long", "meta_too_short"}

    updated_title = 0
    needs_ai = 0
    updated_meta = 0
    manual = 0

    for idx, row in df.iterrows():
        if row["status"] not in ("pending", "title_fetch_404"):
            continue

        # Categories use LLM-generated title and meta (Script 4b) — skip here
        if row["url_type"] == "category":
            continue

        issue_set = {i.strip() for i in row["issue"].split(",") if i.strip()}

        # Fix title if needed and not already processed
        if issue_set & title_issues and row["title_action"] == "":
            new_title, action = fix_title(row, utils)
            df.at[idx, "new_title"] = new_title
            df.at[idx, "title_action"] = action
            if action == "needs_ai":
                needs_ai += 1
            elif action == "manual_review":
                manual += 1
            else:
                updated_title += 1

        # Fix meta length if needed and not already processed
        if issue_set & meta_issues and row["meta_action"] == "":
            new_meta, action = fix_meta(row, utils)
            df.at[idx, "new_meta"] = new_meta
            df.at[idx, "meta_action"] = action
            if action == "manual_review":
                manual += 1
            elif action:
                updated_meta += 1

    df.to_csv(MASTER, index=False, encoding="utf-8")

    print(f"  Title fixes:      {updated_title}")
    print(f"  Needs AI:         {needs_ai}")
    print(f"  Meta fixes:       {updated_meta}")
    print(f"  Manual review:    {manual}")
    print(f"\n  Written to {MASTER.relative_to(BASE_DIR)}")
    print("\nDone.")


if __name__ == "__main__":
    main()
