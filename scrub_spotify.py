#!/usr/bin/env python3
"""
Scrubs Spotify streaming history JSON files, retaining only:
  - date (YYYY-MM-DD from ts)
  - track name, artist, album
  - shuffle and skipped flags

Usage:
  python scrub_spotify.py                  # processes all .json files in current dir
  python scrub_spotify.py file1.json ...   # process specific files
  python scrub_spotify.py -o output.csv    # specify output file (default: spotify_scrubbed.csv)
"""

import json
import csv
import sys
import glob
import argparse
from pathlib import Path


FIELDS = [
    "date",
    "track_name",
    "artist_name",
    "album_name",
    "shuffle",
    "skipped",
]


def extract_record(entry: dict) -> dict:
    ts = entry.get("ts", "")
    date = ts[:10] if ts else ""  # take YYYY-MM-DD only
    return {
        "date": date,
        "track_name": entry.get("master_metadata_track_name"),
        "artist_name": entry.get("master_metadata_album_artist_name"),
        "album_name": entry.get("master_metadata_album_album_name"),
        "shuffle": entry.get("shuffle"),
        "skipped": entry.get("skipped"),
    }


def load_json_file(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


def main():
    parser = argparse.ArgumentParser(description="Scrub Spotify streaming JSON files.")
    parser.add_argument("files", nargs="*", help="JSON files to process")
    parser.add_argument("-o", "--output", default="spotify_scrubbed.csv", help="Output CSV file")
    args = parser.parse_args()

    input_files = args.files or sorted(glob.glob("*.json"))
    if not input_files:
        print("No JSON files found.", file=sys.stderr)
        sys.exit(1)

    records = []
    for path in input_files:
        try:
            entries = load_json_file(path)
            records.extend(extract_record(e) for e in entries)
            print(f"  {path}: {len(entries)} entries")
        except Exception as e:
            print(f"  WARNING: skipping {path} — {e}", file=sys.stderr)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)

    print(f"\nWrote {len(records)} rows to {args.output}")


if __name__ == "__main__":
    main()
