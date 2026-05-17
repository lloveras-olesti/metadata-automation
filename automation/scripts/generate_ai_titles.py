#!/usr/bin/env python3
"""
Script 3b: generate_ai_titles.py
Uses Claude API to generate concise titles for products whose titles
could not be mechanically trimmed to fit within the configured length limits.

Model and length limits are read from config.yaml.

Usage:
    python scripts/generate_ai_titles.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_loader import load_config

try:
    import pandas as pd
    import anthropic
except ImportError:
    sys.exit("Missing dependencies: pip install pandas anthropic")

BASE_DIR = Path(__file__).parent.parent
MASTER = BASE_DIR / "data" / "master_urls.csv"

_cfg = load_config()
MODEL: str = _cfg["ai"]["model"]
TITLE_MIN: int = _cfg["seo_limits"]["title_min"]
TITLE_MAX: int = _cfg["seo_limits"]["title_max"]
LANG_NAMES: dict = _cfg["client"]["language_names"]
CLIENT_NAME: str = _cfg["client"]["name"]

PROMPT_TEMPLATE = """\
You are an SEO copywriter for an online bookstore called "{client_name}".

Write a concise, accurate SEO page title for a product page. Requirements:
- Language: {lang_name}
- Exactly between {min_chars} and {max_chars} characters (spaces included)
- Preserve the key identifying information (book title, author, city, year — in order of importance)
- Do not add quotes, do not explain, return ONLY the title text

Original product name: {title}
"""


def generate_title(client: anthropic.Anthropic, title: str, lang: str, attempt: int = 1) -> str | None:
    """Call Claude API to generate a title. Returns the title or None on failure."""
    extra = ""
    if attempt == 2:
        extra = f"\nCRITICAL: The result MUST be between {TITLE_MIN} and {TITLE_MAX} characters. Count carefully."

    prompt = PROMPT_TEMPLATE.format(
        client_name=CLIENT_NAME,
        lang_name=LANG_NAMES.get(lang, lang),
        min_chars=TITLE_MIN,
        max_chars=TITLE_MAX,
        title=title,
    ) + extra

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        result = message.content[0].text.strip().strip('"').strip("'")
        return result
    except Exception as e:
        print(f"    API error: {e}")
        return None


def main():
    print("Script 3b: generate_ai_titles.py")
    print(f"  Model: {MODEL}")

    df = pd.read_csv(MASTER, encoding="utf-8", dtype=str).fillna("")

    mask = df["title_action"] == "needs_ai"
    targets = df[mask]

    print(f"  Rows to process: {len(targets)}")
    if len(targets) == 0:
        print("  Nothing to do.")
        return

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    ok = 0
    failed = 0

    for idx, row in targets.iterrows():
        title = row["title"]
        lang = row["lang"]

        result = generate_title(client, title, lang, attempt=1)
        time.sleep(0.1)

        if result and TITLE_MIN <= len(result) <= TITLE_MAX:
            df.at[idx, "new_title"] = result
            df.at[idx, "title_action"] = "ai_generated"
            ok += 1
            print(f"  OK  [{len(result):>2}c] {result}")
        else:
            # Retry with stricter prompt
            if result:
                print(f"  RETRY [{len(result)}c out of range]: {result[:60]}")
            result2 = generate_title(client, title, lang, attempt=2)
            time.sleep(0.1)

            if result2 and TITLE_MIN <= len(result2) <= TITLE_MAX:
                df.at[idx, "new_title"] = result2
                df.at[idx, "title_action"] = "ai_generated"
                ok += 1
                print(f"  OK  [{len(result2):>2}c] {result2}")
            else:
                df.at[idx, "title_action"] = "ai_failed"
                failed += 1
                print(f"  FAIL: {title[:60]}")

    df.to_csv(MASTER, index=False, encoding="utf-8")

    print(f"\n  Generated: {ok} | Failed: {failed}")
    print(f"  Written to {MASTER.relative_to(BASE_DIR)}")
    print("\nDone.")


if __name__ == "__main__":
    main()
