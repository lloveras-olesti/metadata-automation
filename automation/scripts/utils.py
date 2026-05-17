"""
utils.py — Shared helpers for the auto-metadata SEO pipeline.

All text-generation logic lives here to keep individual scripts thin.
Client-specific values (brand name, suffix, templates, limits, etc.) are
loaded from config.yaml via config_loader — nothing is hardcoded here.

NOTE: classify_url() uses URL patterns specific to PrestaShop
(/{id}-{slug}.html for products, /{id}-{slug} for categories).
For other CMS platforms, adapt this function to match the target site's
URL structure.
"""

import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from config_loader import load_config

_cfg = load_config()
_client = _cfg["client"]
_brand = _cfg["brand"]
_meta_tpl = _cfg["meta_templates"]
_limits = _cfg["seo_limits"]

# ---------------------------------------------------------------------------
# Constants (derived from config.yaml)
# ---------------------------------------------------------------------------

BASE_DOMAIN: str = _client["base_domain"]
LANGUAGES: list = _client["languages"]

SUFFIX_BRAND: str = _brand["suffix_short"]
SUFFIX_LONG: dict = _brand["suffix_long"]

META_PREFIX: dict = _meta_tpl["prefix"]
META_INFIX: dict = _meta_tpl["infix"]
META_SUFFIX_FULL: dict = _brand["suffix_long"]   # alias for readability in callers
META_SUFFIX_BRAND: str = _brand["suffix_short"]  # alias for readability in callers

TITLE_MIN: int = _limits["title_min"]
TITLE_MAX: int = _limits["title_max"]
META_MIN: int = _limits["meta_min"]
META_MAX: int = _limits["meta_max"]


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def classify_url(url: str) -> str:
    """
    Return 'product', 'category', 'geo', or 'cms'.

    Pattern logic is PrestaShop-specific:
      - geo:      URL path contains /geo/
      - product:  last segment ends with .html and matches /{id}-{slug}.html
      - category: last segment matches /{id}-{slug} (no .html)
      - cms:      everything else
    Adapt this function for other CMS platforms.
    """
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")

    if "/geo/" in path:
        return "geo"

    if path.endswith(".html"):
        last_seg = path.split("/")[-1].replace(".html", "")
        if re.match(r"^\d+-", last_seg):
            return "product"

    last_seg = path.split("/")[-1] if path else ""
    if re.match(r"^\d+-", last_seg):
        return "category"

    return "cms"


def extract_lang(url: str) -> str:
    """
    Extract the language code from URL path.
    Recognises codes defined in config.yaml → client.languages.
    Defaults to the first configured language if none is found.
    """
    parts = urlparse(url).path.strip("/").split("/")
    for part in parts:
        if part in LANGUAGES:
            return part
    return LANGUAGES[0]


def extract_product_id(url: str) -> int | None:
    """Extract numeric product ID from URL slug. Returns None if not found."""
    path = urlparse(url).path
    last = path.rstrip("/").split("/")[-1].replace(".html", "")
    m = re.match(r"^(\d+)-", last)
    return int(m.group(1)) if m else None


def extract_category_id(url: str) -> int | None:
    """Extract numeric category ID from URL slug."""
    path = urlparse(url).path
    last = path.rstrip("/").split("/")[-1]
    m = re.match(r"^(\d+)-", last)
    return int(m.group(1)) if m else None


def extract_cms_id(url: str) -> int | None:
    """
    Extract numeric CMS ID from /content/{id}-{slug} URLs.
    Returns None otherwise.
    This pattern is PrestaShop-specific.
    """
    m = re.search(r"/content/(\d+)[-/]?", urlparse(url).path)
    return int(m.group(1)) if m else None


def extract_url_slug(url: str) -> str:
    """Return the last path segment (before any query string) as a potential link_rewrite slug."""
    path = urlparse(url).path.rstrip("/")
    return path.split("/")[-1] if path else ""


def normalise_url(url: str) -> str:
    """Strip trailing slash, query params, and expand relative URLs to full."""
    url = url.strip()
    if url.startswith("/"):
        url = BASE_DOMAIN + url
    url = url.split("?")[0]  # drop query string (?p=2 pagination variants)
    return url.rstrip("/")


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def strip_brand_suffix(title: str) -> str:
    """Remove trailing brand suffix variants from a title."""
    for lang in LANGUAGES:
        suffix = SUFFIX_LONG.get(lang, "")
        if suffix and title.endswith(suffix):
            return title[: -len(suffix)]
    if title.endswith(SUFFIX_BRAND):
        return title[: -len(SUFFIX_BRAND)]
    return title


def trim_by_dashes(text: str, max_len: int) -> str | None:
    """
    Strip the rightmost ' - {segment}' portions until len(text) <= max_len.
    Returns None if even the base (first segment alone) exceeds max_len.
    """
    if len(text) <= max_len:
        return text

    parts = text.split(" - ")
    while len(parts) > 1 and len(" - ".join(parts)) > max_len:
        parts.pop()

    result = " - ".join(parts)
    return result if len(result) <= max_len else None


# ---------------------------------------------------------------------------
# Title generators (target: TITLE_MIN–TITLE_MAX chars)
# ---------------------------------------------------------------------------

def _fit_title(base: str, lang: str) -> str:
    """
    Given a base string, add the shortest suffix that keeps result in [TITLE_MIN, TITLE_MAX].
    base is assumed to be <= TITLE_MAX chars already.
    """
    with_brand = base + SUFFIX_BRAND
    if TITLE_MIN <= len(with_brand) <= TITLE_MAX:
        return with_brand
    if len(with_brand) < TITLE_MIN:
        with_long = base + SUFFIX_LONG.get(lang, SUFFIX_BRAND)
        return with_long[:TITLE_MAX]
    # with_brand > TITLE_MAX: base alone is within range
    return base


def build_product_title_trimmed(title: str, lang: str) -> str | None:
    """
    Trim a too-long product title using dash-segment removal.
    Strips brand suffix first, then trims, then re-adds suffix.
    Returns None → caller should mark as needs_ai.
    """
    base = strip_brand_suffix(title)
    trimmed = trim_by_dashes(base, TITLE_MAX)
    if trimmed is None:
        return None  # even base is > TITLE_MAX → needs AI
    return _fit_title(trimmed, lang)


def build_product_title_extended(title: str, lang: str) -> str:
    """Extend a too-short product title with brand suffix."""
    base = strip_brand_suffix(title.strip())
    return _fit_title(base, lang)


def build_category_title(label: str, lang: str) -> str:
    """Build title for a category page from its hierarchical label."""
    return _fit_title(label[:TITLE_MAX], lang)


def build_geo_title(geo_name: str, lang: str) -> str:
    """Build title for a geo page. Prefix: 'Literatura de {place}'."""
    base = f"Literatura de {geo_name}"
    return build_category_title(base, lang)


# ---------------------------------------------------------------------------
# Meta description generators (target: META_MIN–META_MAX chars)
# ---------------------------------------------------------------------------

def build_product_meta(h1: str, lang: str) -> str:
    """
    Build meta description for a product page.
    Base = h1; append long suffix; trim if > META_MAX.
    """
    suffix_full = META_SUFFIX_FULL.get(lang, META_SUFFIX_BRAND)
    candidate = h1 + suffix_full
    if len(candidate) <= META_MAX:
        return candidate

    # Try trimming h1 so it fits with full suffix
    max_h1 = META_MAX - len(suffix_full)
    trimmed = trim_by_dashes(h1, max_h1)
    if trimmed:
        return trimmed + suffix_full

    # Try with brand-only suffix
    max_h1_brand = META_MAX - len(META_SUFFIX_BRAND)
    trimmed2 = trim_by_dashes(h1, max_h1_brand)
    if trimmed2:
        return trimmed2 + META_SUFFIX_BRAND

    # Last resort: hard truncate
    return h1[:META_MAX - 3] + "..."


def build_category_meta(label: str, lang: str) -> str:
    """
    Build meta description for a category page.
    Template: {prefix}{label}{infix}{suffix}
    Trims suffixes progressively if > META_MAX.
    """
    prefix = META_PREFIX.get(lang, META_PREFIX.get(LANGUAGES[0], ""))
    infix = META_INFIX.get(lang, META_INFIX.get(LANGUAGES[0], ""))
    suffix_full = META_SUFFIX_FULL.get(lang, META_SUFFIX_BRAND)

    base = f"{prefix}{label}{infix}"

    candidate = base + suffix_full
    if len(candidate) <= META_MAX:
        return candidate

    candidate = base + META_SUFFIX_BRAND
    if len(candidate) <= META_MAX:
        return candidate

    return base[:META_MAX]


def build_geo_meta(geo_name: str, lang: str) -> str:
    """Build meta description for a geo page."""
    label = f"Literatura de {geo_name}"
    return build_category_meta(label, lang)


# ---------------------------------------------------------------------------
# Lookup loader
# ---------------------------------------------------------------------------

def load_lookup(lang: str, base_dir: Path | None = None) -> dict:
    """
    Load category_lookup_{lang}.csv.
    Returns {normalised_full_url: {label, type}}.
    Relative geo URLs are expanded to full URLs.
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent
    path = base_dir / "data" / "lookups" / f"category_lookup_{lang}.csv"

    lookup: dict = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            url = normalise_url(row["url"])
            lookup[url] = {"label": row["label"], "type": row["type"]}
    return lookup


def lookup_label(url: str, lookup: dict) -> str:
    """Return the category label for a URL, or empty string if not found."""
    return lookup.get(normalise_url(url), {}).get("label", "")
