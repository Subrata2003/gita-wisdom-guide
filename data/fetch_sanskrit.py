"""
One-time script: download Sanskrit (Devanagari) for all Gita verses
and save to data/sanskrit_lookup.json.

Source: vedicscriptures.github.io  (free, no API key required)

Run once from the project root:
    python data/fetch_sanskrit.py

Output: data/sanskrit_lookup.json
  Keys  : "chapter_verse"  e.g. "1_1", "2_47"
  Values: { "sanskrit": "<Devanagari>", "transliteration": "<IAST>" }
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "https://vedicscriptures.github.io/slok/{chapter}/{verse}/"

# All 18 chapters with their verse counts
CHAPTER_VERSES = {
    1: 47, 2: 72, 3: 43, 4: 42, 5: 29, 6: 47, 7: 30, 8: 28,
    9: 34, 10: 42, 11: 55, 12: 20, 13: 35, 14: 27, 15: 20,
    16: 24, 17: 28, 18: 78,
}

OUTPUT = Path(__file__).parent / "sanskrit_lookup.json"


def fetch_verse(chapter: int, verse: int):
    url = BASE_URL.format(chapter=chapter, verse=verse)
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
        return {
            "sanskrit":        data.get("slok", "").strip(),
            "transliteration": data.get("transliteration", "").strip(),
        }
    except Exception as e:
        print(f"  SKIP {chapter}.{verse}: {type(e).__name__}")
        return None


def main():
    lookup = {}
    total = sum(CHAPTER_VERSES.values())
    done = 0

    print(f"Fetching {total} verses from vedicscriptures.github.io ...")

    for ch, verses in CHAPTER_VERSES.items():
        for v in range(1, verses + 1):
            key = f"{ch}_{v}"
            result = fetch_verse(ch, v)
            if result:
                lookup[key] = result
            done += 1
            if done % 20 == 0:
                print(f"  {done}/{total} fetched ...")
            time.sleep(0.15)

    OUTPUT.write_text(json.dumps(lookup, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone! Saved {len(lookup)} entries -> {OUTPUT}")
    print("Restart the backend -- Sanskrit will appear in verse cards automatically.")


if __name__ == "__main__":
    main()
