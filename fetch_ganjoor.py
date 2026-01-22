#!/usr/bin/env python3
"""
Simple Ganjoor Fetcher - fetches ghazals from ganjoor.net website
Works by scraping the HTML pages directly.

Usage:
    python fetch_ganjoor.py --start 1 --count 5 --output real_ghazals.json
"""

import requests
import json
import re
import time
import argparse
from bs4 import BeautifulSoup

BASE_URL = "https://ganjoor.net/moulavi/shams/ghazalsh/sh"

def fetch_ghazal(ghazal_num: int) -> dict | None:
    """Fetch a single ghazal from Ganjoor website."""
    url = f"{BASE_URL}{ghazal_num}/"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the poem content
        # Ganjoor uses specific classes for poem content
        poem_div = soup.find('div', class_='b')
        if not poem_div:
            # Try alternative selectors
            poem_div = soup.find('div', class_='poem-content')
        if not poem_div:
            poem_div = soup.find('article')

        if not poem_div:
            print(f"  Could not find poem content for ghazal {ghazal_num}")
            return None

        # Extract verses
        # Ganjoor typically has verses in <p> tags with class 'm1' and 'm2' for hemistichs
        verses = []

        # Try to find verse pairs
        m1_tags = poem_div.find_all('p', class_='m1')  # First hemistich
        m2_tags = poem_div.find_all('p', class_='m2')  # Second hemistich

        if m1_tags and m2_tags:
            for m1, m2 in zip(m1_tags, m2_tags):
                verses.append({
                    "hemistich1": m1.get_text(strip=True),
                    "hemistich2": m2.get_text(strip=True)
                })
        else:
            # Alternative: look for all verse lines
            verse_tags = poem_div.find_all('p', class_=re.compile(r'm\d'))
            if verse_tags:
                for i in range(0, len(verse_tags), 2):
                    if i + 1 < len(verse_tags):
                        verses.append({
                            "hemistich1": verse_tags[i].get_text(strip=True),
                            "hemistich2": verse_tags[i + 1].get_text(strip=True)
                        })
            else:
                # Last resort: get all text and try to parse
                all_text = poem_div.get_text(separator='\n', strip=True)
                lines = [l.strip() for l in all_text.split('\n') if l.strip()]
                for i in range(0, len(lines), 2):
                    if i + 1 < len(lines):
                        verses.append({
                            "hemistich1": lines[i],
                            "hemistich2": lines[i + 1]
                        })

        if not verses:
            print(f"  Could not extract verses for ghazal {ghazal_num}")
            return None

        # Try to get the title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else f"غزل شماره {ghazal_num}"

        return {
            "number": ghazal_num,
            "ganjoor_url": url,
            "title": title,
            "meter": "",  # Would need additional parsing
            "rhyme": "",  # Would need additional parsing
            "verses": verses,
            "notes": ""
        }

    except requests.RequestException as e:
        print(f"  Error fetching ghazal {ghazal_num}: {e}")
        return None


def fetch_ghazals(start: int, count: int, delay: float = 1.0) -> list:
    """Fetch multiple ghazals."""
    ghazals = []

    for i in range(start, start + count):
        print(f"Fetching ghazal {i}...", end=" ")
        ghazal = fetch_ghazal(i)

        if ghazal:
            ghazals.append(ghazal)
            print(f"✓ ({len(ghazal['verses'])} verses)")
        else:
            print("✗")

        # Be respectful to the server
        time.sleep(delay)

    return ghazals


def save_ghazals(ghazals: list, output_file: str):
    """Save ghazals to JSON file."""
    data = {
        "source": "Divan-e Shams-e Tabrizi (Divan-e Kabir)",
        "edition": "Ganjoor.net",
        "fetched_from": "ganjoor.net/moulavi/shams/ghazalsh/",
        "note": "Fetched directly from Ganjoor website",
        "ghazals": ghazals
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(ghazals)} ghazals to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Fetch ghazals from Ganjoor website")
    parser.add_argument("--start", "-s", type=int, default=1, help="Starting ghazal number")
    parser.add_argument("--count", "-c", type=int, default=5, help="Number of ghazals to fetch")
    parser.add_argument("--output", "-o", default="real_ghazals.json", help="Output JSON file")
    parser.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between requests (seconds)")

    args = parser.parse_args()

    print(f"Fetching ghazals {args.start} to {args.start + args.count - 1} from Ganjoor...")
    ghazals = fetch_ghazals(args.start, args.count, args.delay)

    if ghazals:
        save_ghazals(ghazals, args.output)
    else:
        print("No ghazals fetched.")


if __name__ == "__main__":
    main()
