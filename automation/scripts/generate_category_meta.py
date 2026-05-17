#!/usr/bin/env python3
"""
Script 4b: generate_category_meta.py
Generates SEO-optimised meta titles and meta descriptions for high-priority
pages using the Claude API.

The target page type is configured via config.yaml → seo_generation.relevant_page_type
(default: "category"). To process a different page type (e.g. "geo"), change that
value and re-run the script.

All prompt parameters — business description, keyword pool, CTAs, brand rules —
are assembled from config.yaml. No client-specific values are hardcoded.

Usage:
    python scripts/generate_category_meta.py
    python scripts/generate_category_meta.py --dry-run   # preview, do not save
"""

import argparse
import json
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
META_MIN: int = _cfg["seo_limits"]["meta_min"]
META_MAX: int = _cfg["seo_limits"]["meta_max"]
RELEVANT_PAGE_TYPE: str = _cfg["seo_generation"]["relevant_page_type"]
LANG_NAMES: dict = _cfg["client"]["language_names"]


# ---------------------------------------------------------------------------
# Prompt assembly (reads all client values from config.yaml)
# ---------------------------------------------------------------------------

def _format_keyword_pool(keyword_pool: dict, languages: list, lang_names: dict) -> str:
    """Format keyword pool for all configured languages."""
    lines = []
    for lang in languages:
        if lang in keyword_pool:
            lang_name = lang_names.get(lang, lang)
            terms = ", ".join(keyword_pool[lang])
            lines.append(f"- {lang_name}: {terms}")
    return "\n".join(lines)


def _format_ctas(ctas: dict, languages: list, lang_names: dict) -> str:
    """Format call-to-action phrases for the prompt."""
    parts = []
    for lang in languages:
        if lang in ctas:
            lang_name = lang_names.get(lang, lang)
            examples = ", ".join(f'"{c}"' for c in ctas[lang])
            parts.append(f"{lang_name} examples: {examples}")
    return "; ".join(parts)


def build_prompt(label: str, lang: str, retry: bool = False) -> str:
    """
    Assemble the full prompt for one page, using values from config.yaml.
    All client-specific content comes from the config — nothing is hardcoded here.
    """
    client = _cfg["client"]
    brand = _cfg["brand"]
    seo_gen = _cfg["seo_generation"]
    lang_names = client["language_names"]
    languages = client["languages"]

    lang_name = lang_names.get(lang, lang)
    client_name = client["name"]
    client_description = client["description"].strip()
    brand_suffix = brand["suffix_short"]
    include_brand = seo_gen.get("include_brand_in_meta_description", False)

    keyword_pool_str = _format_keyword_pool(
        seo_gen["keyword_pool"], languages, lang_names
    )
    ctas_str = _format_ctas(seo_gen["ctas"], languages, lang_names)

    brand_in_meta_rule = (
        f"- Include the store name '{client_name}' naturally if space allows"
        if include_brand
        else "- Do not include the store name — use the space for keywords and CTA instead"
    )

    prompt = f"""\
You are an expert SEO copywriter for "{client_name}", {client_description}

Write an SEO-optimised meta title and meta description for one of the shop's \
{RELEVANT_PAGE_TYPE} pages on the website.

Category: {label}
Language: {lang_name}

GENERIC KEYWORD POOL — these terms describe the shop and apply to all pages. \
Use 1–2 of the most natural fits for this specific category; do not force all of them in:
{keyword_pool_str}
Use only the terms that match the page language. Blend naturally — avoid keyword stuffing.

META TITLE — must be {TITLE_MIN}–{TITLE_MAX} characters (spaces included):
- Lead with the primary keyword for this category
- Append "{brand_suffix}" if the full result is within {TITLE_MAX} characters; \
if it does not fit, omit it entirely — never shorten or truncate the brand name
- "{client_name}" is never translated
- No trailing punctuation

META DESCRIPTION — must be {META_MIN}–{META_MAX} characters (spaces included):
- Open with the primary keyword or a close natural variant
- Weave in 1–2 terms from the generic keyword pool where they fit naturally
- Include a call to action ({ctas_str})
{brand_in_meta_rule}
- No trailing punctuation

Count every character carefully before answering, including spaces.
Respond ONLY with valid JSON, no markdown, no explanation:
{{"meta_title": "...", "meta_description": "..."}}"""

    if retry:
        prompt += f"""

IMPORTANT: your previous response had a character length error. \
Count each character individually. \
meta_title: {TITLE_MIN}–{TITLE_MAX} chars. meta_description: {META_MIN}–{META_MAX} chars."""

    return prompt


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def call_api(client: anthropic.Anthropic, prompt: str) -> tuple[str, str] | None:
    """Call Claude API. Returns (meta_title, meta_description) or None on error."""
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        data = json.loads(raw)
        return data.get("meta_title", "").strip(), data.get("meta_description", "").strip()
    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"    API error: {e}")
        return None


def is_valid(title: str, meta: str) -> bool:
    return (
        TITLE_MIN <= len(title) <= TITLE_MAX
        and META_MIN <= len(meta) <= META_MAX
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import utils

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview output, do not save")
    args = parser.parse_args()

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    print(f"Script 4b: generate_category_meta.py  [{mode}]")
    print(f"  Model:             {MODEL}")
    print(f"  Target page type:  {RELEVANT_PAGE_TYPE}")
    if args.dry_run:
        print("  Pass without --dry-run to save results.")
    print()

    df = pd.read_csv(MASTER, encoding="utf-8", dtype=str).fillna("")

    targets = df[df["url_type"] == RELEVANT_PAGE_TYPE]
    print(f"  Rows to process ({RELEVANT_PAGE_TYPE}): {len(targets)}")

    if len(targets) == 0:
        print("  Nothing to do.")
        return

    client = anthropic.Anthropic()

    ok = 0
    fallback = 0
    no_label = 0

    for idx, row in targets.iterrows():
        label = row["category_label"]
        lang = row["lang"]
        url = row["url"]

        if not label:
            print(f"  SKIP (no label): {url[-70:]}")
            no_label += 1
            continue

        title = meta = None
        action = "ai_seo"

        # Attempt 1
        result = call_api(client, build_prompt(label, lang, retry=False))
        time.sleep(0.15)

        if result and is_valid(*result):
            title, meta = result
        else:
            # Attempt 2 with stricter prompt
            if result:
                t, m = result
                print(f"  RETRY [{len(t)}c title / {len(m)}c meta]: {label}")
            result2 = call_api(client, build_prompt(label, lang, retry=True))
            time.sleep(0.15)

            if result2 and is_valid(*result2):
                title, meta = result2
            else:
                # Fallback to deterministic template — no data loss
                title = utils.build_category_title(label, lang)
                meta = utils.build_category_meta(label, lang)
                action = "ai_seo_fallback"
                fallback += 1
                print(f"  FALLBACK (template): {label[:55]}")

        if action == "ai_seo":
            ok += 1
            print(f"  OK  [{len(title):>2}c / {len(meta):>3}c]  {label[:35]:<35} → {title}")

        if not args.dry_run:
            df.at[idx, "new_title"] = title
            df.at[idx, "new_meta"] = meta
            df.at[idx, "title_action"] = action
            df.at[idx, "meta_action"] = action

    if not args.dry_run:
        df.to_csv(MASTER, index=False, encoding="utf-8")
        print(f"\n  Written to {MASTER.relative_to(BASE_DIR)}")

    print(f"\n  Generated (AI):       {ok}")
    print(f"  Fallback (template):  {fallback}")
    print(f"  Skipped (no label):   {no_label}")
    print("\nDone.")


if __name__ == "__main__":
    main()
