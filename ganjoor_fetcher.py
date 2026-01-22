#!/usr/bin/env python3
"""
Ganjoor API Fetcher for Divan-e Kabir

This script fetches Persian poetry from the Ganjoor.net API.
Use this to populate the source data for translation.

Usage:
    python ganjoor_fetcher.py --poet moulavi --category shams --limit 100
    python ganjoor_fetcher.py --poem-id 12345
"""

import requests
import json
import argparse
import time
from typing import Optional

BASE_URL = "https://api.ganjoor.net/api/ganjoor"

# Known poet IDs from Ganjoor
POETS = {
    "moulavi": 2,      # Rumi
    "hafez": 3,
    "saadi": 4,
    "ferdowsi": 5,
    "khayyam": 6,
    "attar": 7,
}

# Rumi's work categories
RUMI_CATEGORIES = {
    "masnavi": "masnavi",
    "shams": "shams",      # Divan-e Shams
    "ghazals": "shams",    # Alias
}


class GanjoorFetcher:
    def __init__(self, delay: float = 0.5):
        """
        Initialize the fetcher.

        Args:
            delay: Seconds to wait between API calls (be respectful!)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "DivanTranslationProject/1.0"
        })

    def get_poets(self) -> list:
        """Get list of all poets."""
        response = self.session.get(f"{BASE_URL}/poets")
        response.raise_for_status()
        return response.json()

    def get_poet_info(self, poet_id: int) -> dict:
        """Get detailed info about a poet."""
        response = self.session.get(f"{BASE_URL}/poet/{poet_id}")
        response.raise_for_status()
        return response.json()

    def get_category(self, category_url: str) -> dict:
        """
        Get poems in a category.

        Args:
            category_url: The URL path like "/moulavi/shams"
        """
        # Remove leading slash if present
        if category_url.startswith("/"):
            category_url = category_url[1:]

        response = self.session.get(f"{BASE_URL}/cat?url={category_url}&poems=true")
        response.raise_for_status()
        return response.json()

    def get_poem(self, poem_id: int) -> dict:
        """Get a specific poem by ID."""
        response = self.session.get(f"{BASE_URL}/poem/{poem_id}")
        response.raise_for_status()
        return response.json()

    def get_poem_by_url(self, url: str) -> dict:
        """Get a poem by its URL path."""
        if url.startswith("/"):
            url = url[1:]
        response = self.session.get(f"{BASE_URL}/poem?url={url}")
        response.raise_for_status()
        return response.json()

    def search_poems(self, query: str, poet_id: Optional[int] = None, page: int = 1) -> dict:
        """Search for poems containing text."""
        params = {
            "term": query,
            "pageNumber": page,
            "pageSize": 20
        }
        if poet_id:
            params["poetId"] = poet_id

        response = self.session.get(f"{BASE_URL}/poems/search", params=params)
        response.raise_for_status()
        return response.json()

    def fetch_divan_ghazals(self, start: int = 1, limit: int = 100) -> list:
        """
        Fetch ghazals from Rumi's Divan-e Shams.

        This navigates the category structure to get individual poems.
        """
        ghazals = []

        # First, get the Divan-e Shams category structure
        print("Fetching Divan-e Shams category structure...")
        try:
            cat_info = self.get_category("moulavi/shams")
        except requests.RequestException as e:
            print(f"Error fetching category: {e}")
            return ghazals

        # The Divan is organized by meter, then individual ghazals
        # Navigate subcategories to find poems
        if "cat" in cat_info and "children" in cat_info["cat"]:
            for meter_cat in cat_info["cat"]["children"]:
                if len(ghazals) >= limit:
                    break

                print(f"Fetching from meter: {meter_cat.get('title', 'Unknown')}")
                time.sleep(self.delay)

                try:
                    meter_info = self.get_category(meter_cat["fullUrl"])

                    if "poems" in meter_info:
                        for poem in meter_info["poems"]:
                            if len(ghazals) >= limit:
                                break

                            ghazal = self._parse_poem(poem, meter_cat.get("title", ""))
                            if ghazal:
                                ghazals.append(ghazal)
                                print(f"  Fetched ghazal #{ghazal['number']}")
                            time.sleep(self.delay)

                except requests.RequestException as e:
                    print(f"  Error: {e}")
                    continue

        return ghazals

    def _parse_poem(self, poem_data: dict, meter: str = "") -> Optional[dict]:
        """Parse API poem data into our standard format."""
        try:
            verses = []

            # Ganjoor returns verses as a flat list
            # Each beyt (couplet) has two hemistichs
            if "verses" in poem_data:
                verse_list = poem_data["verses"]
                for i in range(0, len(verse_list), 2):
                    if i + 1 < len(verse_list):
                        verses.append({
                            "hemistich1": verse_list[i].get("text", ""),
                            "hemistich2": verse_list[i + 1].get("text", "")
                        })

            if not verses:
                return None

            # Extract rhyme from last word of last hemistich
            last_verse = verses[-1]["hemistich2"] if verses else ""
            rhyme = self._extract_rhyme(last_verse)

            return {
                "number": poem_data.get("id", 0),
                "ganjoor_id": poem_data.get("id"),
                "title": poem_data.get("title", ""),
                "meter": meter,
                "rhyme": rhyme,
                "verses": verses,
                "url": poem_data.get("fullUrl", ""),
                "notes": ""
            }

        except Exception as e:
            print(f"Error parsing poem: {e}")
            return None

    def _extract_rhyme(self, text: str) -> str:
        """Extract approximate rhyme pattern from text."""
        # Simple extraction of last few characters
        words = text.strip().split()
        if words:
            last_word = words[-1]
            if len(last_word) >= 2:
                return f"-{last_word[-2:]}"
        return ""


def save_ghazals(ghazals: list, output_file: str):
    """Save fetched ghazals to JSON file."""
    data = {
        "source": "Divan-e Shams-e Tabrizi (Divan-e Kabir)",
        "edition": "Ganjoor.net (based on Foruzanfar edition)",
        "fetched_from": "api.ganjoor.net",
        "note": "Fetched via Ganjoor API",
        "ghazals": ghazals
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(ghazals)} ghazals to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Fetch Persian poetry from Ganjoor API")
    parser.add_argument("--limit", "-l", type=int, default=100, help="Number of ghazals to fetch")
    parser.add_argument("--output", "-o", default="ganjoor_ghazals.json", help="Output JSON file")
    parser.add_argument("--delay", "-d", type=float, default=0.5, help="Delay between API calls (seconds)")
    parser.add_argument("--poem-id", type=int, help="Fetch a specific poem by ID")
    parser.add_argument("--search", "-s", help="Search for poems containing text")

    args = parser.parse_args()

    fetcher = GanjoorFetcher(delay=args.delay)

    if args.poem_id:
        # Fetch single poem
        print(f"Fetching poem ID {args.poem_id}...")
        poem = fetcher.get_poem(args.poem_id)
        print(json.dumps(poem, ensure_ascii=False, indent=2))

    elif args.search:
        # Search poems
        print(f"Searching for '{args.search}'...")
        results = fetcher.search_poems(args.search, poet_id=POETS["moulavi"])
        print(json.dumps(results, ensure_ascii=False, indent=2))

    else:
        # Fetch collection
        print(f"Fetching up to {args.limit} ghazals from Divan-e Shams...")
        ghazals = fetcher.fetch_divan_ghazals(limit=args.limit)
        save_ghazals(ghazals, args.output)


if __name__ == "__main__":
    main()
