#!/usr/bin/env python3
"""
Ganjoor API Fetcher for Divan-e Kabir

This script fetches Persian poetry from the Ganjoor.net API.
Use this to populate the source data for translation.

Usage:
    python ganjoor_fetcher.py --start 1 --count 5 --output real_ghazals.json
    python ganjoor_fetcher.py --poem-id 12345
"""

import requests
import json
import argparse
import time
from typing import Optional

BASE_URL = "https://api.ganjoor.net/api/ganjoor"

# Known poet IDs from Ganjoor (verified from /api/ganjoor/poets endpoint)
POETS = {
    "moulavi": 5,      # Rumi - جلال الدین محمد مولوی
    "hafez": 2,        # حافظ
    "saadi": 28,       # سعدی
    "ferdowsi": 24,    # فردوسی
    "khayyam": 18,     # خیام
    "attar": 44,       # عطار
}

# Rumi's work categories
RUMI_CATEGORIES = {
    "masnavi": "masnavi",
    "shams": "shams",      # Divan-e Shams
    "ghazals": "shams",    # Alias
}


class GanjoorFetcher:
    def __init__(self, delay: float = 1.0):
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

    def get_page(self, url_path: str) -> dict:
        """
        Get a page by its URL path using the page endpoint.

        Args:
            url_path: The URL path like "/moulavi/shams/ghazalsh/sh1"
        """
        # Remove leading slash if present
        if url_path.startswith("/"):
            url_path = url_path[1:]

        response = self.session.get(f"{BASE_URL}/page?url={url_path}")
        response.raise_for_status()
        return response.json()

    def get_poem(self, poem_id: int) -> dict:
        """Get a specific poem by ID."""
        response = self.session.get(f"{BASE_URL}/poem/{poem_id}")
        response.raise_for_status()
        return response.json()

    def get_poem_by_url(self, url: str) -> dict:
        """Get a poem by its URL path using the page endpoint."""
        return self.get_page(url)

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

    def get_ghazal_index(self) -> list:
        """
        Get the full index of ghazals from category 99.
        Returns list of {id, title, urlSlug, excerpt} for all 3230 ghazals.
        """
        response = self.session.get(f"{BASE_URL}/cat/99")
        response.raise_for_status()
        data = response.json()
        return data.get("cat", {}).get("poems", [])

    def fetch_ghazal_by_poem_id(self, poem_id: int) -> Optional[dict]:
        """
        Fetch a specific ghazal by its Ganjoor poem ID.
        """
        try:
            response = self.session.get(f"{BASE_URL}/poem/{poem_id}")
            response.raise_for_status()
            poem_data = response.json()
            return self._parse_poem_response(poem_data)
        except requests.RequestException as e:
            print(f"  Error fetching poem {poem_id}: {e}")
            return None

    def fetch_ghazal_by_number(self, ghazal_num: int, index: list = None) -> Optional[dict]:
        """
        Fetch a specific ghazal by its number (1-3230).

        If index is provided, uses it to look up the poem ID.
        Otherwise fetches the index first (slower for single lookups).
        """
        if index is None:
            index = self.get_ghazal_index()

        # Find the poem with matching number (ghazal_num corresponds to position)
        if ghazal_num < 1 or ghazal_num > len(index):
            print(f"  Ghazal {ghazal_num} out of range (1-{len(index)})")
            return None

        poem_info = index[ghazal_num - 1]  # 0-indexed
        poem_id = poem_info["id"]

        return self.fetch_ghazal_by_poem_id(poem_id)

    def fetch_divan_ghazals(self, start: int = 1, count: int = 100) -> list:
        """
        Fetch ghazals from Rumi's Divan-e Shams by number range.

        First fetches the index to get poem IDs, then fetches each poem.
        """
        ghazals = []

        print("Fetching ghazal index from Ganjoor...")
        try:
            index = self.get_ghazal_index()
            print(f"Found {len(index)} ghazals in index")
        except requests.RequestException as e:
            print(f"Error fetching index: {e}")
            return ghazals

        end = min(start + count - 1, len(index))
        print(f"Fetching ghazals {start} to {end}...")

        for num in range(start, end + 1):
            print(f"Fetching ghazal #{num}...", end=" ", flush=True)

            ghazal = self.fetch_ghazal_by_number(num, index)

            if ghazal:
                ghazals.append(ghazal)
                print(f"✓ ({len(ghazal['verses'])} verses)")
            else:
                print("✗")

            # Be respectful to the server
            time.sleep(self.delay)

        return ghazals

    def _parse_poem_response(self, poem_data: dict) -> Optional[dict]:
        """Parse the /poem/{id} API response into our standard ghazal format."""
        try:
            if not poem_data:
                return None

            # Extract ghazal number from title (e.g., "غزل شمارهٔ ۱")
            title = poem_data.get("title", "")
            ghazal_num = self._extract_ghazal_number(title)

            # Parse verses from plainText (cleaner than HTML)
            plain_text = poem_data.get("plainText", "")
            verses = self._parse_plain_text_verses(plain_text)

            if not verses:
                return None

            # Extract rhyme from last hemistich
            last_hemistich = verses[-1]["hemistich2"] if verses else ""
            rhyme = self._extract_rhyme(last_hemistich)

            # Get meter if available
            meter = poem_data.get("rhythm", "")

            return {
                "number": ghazal_num,
                "ganjoor_id": poem_data.get("id"),
                "ganjoor_url": f"https://ganjoor.net{poem_data.get('fullUrl', '')}",
                "title": title,
                "full_title": poem_data.get("fullTitle", ""),
                "meter": meter,
                "rhyme": rhyme,
                "verses": verses,
                "plain_text": plain_text,
                "notes": ""
            }

        except Exception as e:
            print(f"Error parsing poem response: {e}")
            return None

    def _extract_ghazal_number(self, title: str) -> int:
        """Extract ghazal number from title like 'غزل شمارهٔ ۱'."""
        import re
        # Convert Persian digits to Arabic
        persian_to_arabic = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
        title_ascii = title.translate(persian_to_arabic)
        # Find number
        match = re.search(r'\d+', title_ascii)
        return int(match.group()) if match else 0

    def _parse_plain_text_verses(self, plain_text: str) -> list:
        """
        Parse verses from plainText format.

        The plainText format has each hemistich on its own line.
        Lines alternate: hemistich1, hemistich2, hemistich1, hemistich2...
        So we pair them up to form couplets (beyts).
        """
        import re
        verses = []

        # Normalize line endings and split
        text = plain_text.replace('\r\n', '\n').replace('\r', '\n')
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Pair up lines into couplets
        for i in range(0, len(lines), 2):
            hemistich1 = lines[i] if i < len(lines) else ""
            hemistich2 = lines[i + 1] if i + 1 < len(lines) else ""

            if hemistich1:  # At least first hemistich must exist
                verses.append({
                    "hemistich1": hemistich1,
                    "hemistich2": hemistich2
                })

        return verses

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
    parser.add_argument("--start", "-s", type=int, default=1, help="Starting ghazal number")
    parser.add_argument("--count", "-c", type=int, default=5, help="Number of ghazals to fetch")
    parser.add_argument("--output", "-o", default="real_ghazals.json", help="Output JSON file")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between API calls (seconds)")
    parser.add_argument("--ghazal", "-g", type=int, help="Fetch a specific ghazal by number")
    parser.add_argument("--search", help="Search for poems containing text")
    parser.add_argument("--debug", action="store_true", help="Print raw API response")

    args = parser.parse_args()

    fetcher = GanjoorFetcher(delay=args.delay)

    if args.ghazal:
        # Fetch single ghazal by number
        print(f"Fetching ghazal #{args.ghazal}...")

        # First get the index to find poem ID
        index = fetcher.get_ghazal_index()
        if args.ghazal < 1 or args.ghazal > len(index):
            print(f"Ghazal number out of range (1-{len(index)})")
            return

        poem_id = index[args.ghazal - 1]["id"]
        print(f"Poem ID: {poem_id}")

        if args.debug:
            # Print raw API response for debugging
            response = fetcher.session.get(f"{BASE_URL}/poem/{poem_id}")
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        else:
            ghazal = fetcher.fetch_ghazal_by_poem_id(poem_id)
            if ghazal:
                print(json.dumps(ghazal, ensure_ascii=False, indent=2))
            else:
                print("Failed to fetch ghazal")

    elif args.search:
        # Search poems
        print(f"Searching for '{args.search}'...")
        results = fetcher.search_poems(args.search, poet_id=POETS["moulavi"])
        print(json.dumps(results, ensure_ascii=False, indent=2))

    else:
        # Fetch collection
        print(f"Fetching ghazals {args.start} to {args.start + args.count - 1}...")
        ghazals = fetcher.fetch_divan_ghazals(start=args.start, count=args.count)
        save_ghazals(ghazals, args.output)


if __name__ == "__main__":
    main()
