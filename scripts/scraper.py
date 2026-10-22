#!/usr/bin/env python3
"""
Atlas Directory — Automated Scraper Pipeline
=============================================
Scrapes public listings, cleans/deduplicates, and writes
structured data to src/data/listings.json.

Run locally:
  python3 scripts/scraper.py

Run via GitHub Actions cron (daily):
  .github/workflows/daily-update.yml

Dependencies (added to requirements.txt):
  requests
  beautifulsoup4
  charset-normalizer
"""

from __future__ import annotations

import json
import os
import re
import sys
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "src" / "data" / "listings.json"

HTTP_TIMEOUT = 20
MAX_RETRIES = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

LOG = logging.getLogger("scraper")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Generate a URL-friendly slug from a title."""
    t = text.lower().strip()
    t = re.sub(r"[^a-z0-9\s-]", "", t)
    t = re.sub(r"[\s_]+", "-", t)
    t = re.sub(r"-+", "-", t).strip("-")
    return t[:80] or "annonce"


def clean_string(text: str | None) -> str:
    """Normalize whitespace and trim."""
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def dedupe_by_id(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the most recent item per unique id."""
    seen: dict[str, dict[str, Any]] = {}
    for item in items:
        item_id = item.get("id")
        if not item_id:
            continue
        if item_id not in seen:
            seen[item_id] = item
        else:
            existing = seen[item_id]
            try:
                if item.get("updatedAt", "") > existing.get("updatedAt", ""):
                    seen[item_id] = item
            except Exception:
                # If dates are equal or missing, keep first
                pass
    return list(seen.values())


def generate_id(row: dict[str, Any]) -> str:
    """Generate a stable unique id from key fields."""
    raw = f"{row.get('category','')}|{row.get('city','')}|{row.get('title','')}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


# ---------------------------------------------------------------------------
# Placeholder: real source scraping would go here
# ---------------------------------------------------------------------------

def fetch_sources() -> list[dict[str, Any]]:
    """
    In a real deployment, replace this with actual requests + BeautifulSoup
    calls against the target sites. This function returns a list of raw
    dicts that get cleaned and written to listings.json.
    """
    # Example: pseudo-scraping a source site
    # sources = [
    #     {"url": "https://example-source.ma/listings?category=car&city=casablanca"},
    #     ...
    # ]
    # fetched = []
    # for src in sources:
    #     resp = requests.get(src["url"], headers={"User-Agent": USER_AGENT}, timeout=HTTP_TIMEOUT)
    #     resp.raise_for_status()
    #     soup = BeautifulSoup(resp.text, "html.parser")
    #     for row in soup.select(".listing-row"):
    #         fetched.append({
    #             "title": clean_string(row.select_one(".title").get_text()),
    #             "city": ...,
    #             ...
    #         })
    # return fetched

    return []


# ---------------------------------------------------------------------------
# Demo data injection (used when no live scraping is configured yet)
# ---------------------------------------------------------------------------

def load_demo_data() -> list[dict[str, Any]]:
    """Load demo data from the existing listings.json if present."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
        except (json.JSONDecodeError, OSError):
            LOG.warning("Existing listings.json is invalid; using empty demo set")
    return []


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_pipeline() -> list[dict[str, Any]]:
    """
    1. Fetch raw listings from configured sources.
    2. (If no sources configured, keep existing demo data.)
    3. Clean, normalize, assign ids, deduplicate.
    4. Write to src/data/listings.json.
    """
    new_items: list[dict[str, Any]] = []

    # Try live scraping first
    try:
        raw = fetch_sources()
        if raw:
            LOG.info("Fetched %d raw listings from sources", len(raw))
            new_items.extend(raw)
    except Exception as e:
        LOG.info("No live sources configured or fetch failed (non-fatal): %s", e)

    # If nothing scraped, preserve existing demo data
    if not new_items:
        LOG.info("No new listings fetched; keeping existing demo data")
        return load_demo_data()

    # Clean & normalize
    cleaned: list[dict[str, Any]] = []
    for item in new_items:
        title = clean_string(item.get("title") or item.get("name") or "")
        if not title:
            continue

        city = clean_string(item.get("city") or "").title()
        if not city:
            city = "Casablanca"

        category = clean_string(item.get("category") or "car")

        price_text = clean_string(item.get("price") or "")
        try:
            price_num = int(re.search(r"\d+", price_text).group()) if re.search(r"\d+", price_text) else 0
        except Exception:
            price_num = 0

        cleaned.append({
            "id": generate_id(item),
            "category": category,
            "categoryName": category.title(),
            "city": city,
            "slug": slugify(title),
            "title": title,
            "excerpt": clean_string(item.get("description") or item.get("excerpt") or ""),
            "price": price_num,
            "priceLabel": f"{price_num} DH",
            "priceCurrency": "MAD",
            "availability": "InStock",
            "rating": item.get("rating", None),
            "reviewCount": item.get("reviewCount", None),
            "features": item.get("features", []) or [],
            "provider": {
                "name": clean_string(item.get("provider", {}).get("name") or "Provider"),
                "type": item.get("provider", {}).get("type", "LocalBusiness"),
                "telephone": clean_string(item.get("provider", {}).get("telephone")),
                "address": clean_string(item.get("provider", {}).get("address")),
                "url": item.get("provider", {}).get("url"),
            } if item.get("provider") else None,
            "seo": {
                "description": clean_string(item.get("seo", {}).get("description") or title),
                "keywords": clean_string(item.get("seo", {}).get("keywords") or title),
            },
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        })

    # Deduplicate by id
    deduped = dedupe_by_id(cleaned)
    return deduped


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    listings = run_pipeline()
    if not listings:
        LOG.warning("No listings available; nothing written")
        sys.exit(0)

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(listings, f, indent=2, ensure_ascii=False)

    LOG.info("Wrote %d listings to %s", len(listings), DATA_FILE)


if __name__ == "__main__":
    main()
