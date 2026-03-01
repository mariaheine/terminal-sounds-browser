#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

from src.logger import Logger
from src.bbc_categories import BBCCategories
from src.bbc_sounds_data import BBCSounds
from src.bbc_sound_downloader import BBCSoundDownloader
from src.constants import SOUNDS_CACHE_DIR

version = "0.1.0"

headers = {
    f"User-Agent": "bbc-sound-browser/{version} (educational project; respectful scraper; browsing samples and downloading favourites; no bulk download)",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def main():
    parser = argparse.ArgumentParser(description="Sound Effect Browser")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # TODO make notes on python args parsers
    # bbc categories subparser
    bbc_categories_parser = subparsers.add_parser("bbc_get_categories")

    toggle_favourite_parser = subparsers.add_parser("toggle_favourite")
    toggle_favourite_parser.add_argument("sound_id")

    is_favourite_parser = subparsers.add_parser("is_favourite")
    is_favourite_parser.add_argument("sound_id")

    bbc_download_preview_parser = subparsers.add_parser("bbc_download_preview_sound")
    bbc_download_preview_parser.add_argument("sound_id")
    bbc_download_preview_parser.add_argument("category")

    # bbc sounds subparser
    bbc_sounds_parser = subparsers.add_parser("bbc_get_sounds_data")
    bbc_sounds_parser.add_argument("category")
    bbc_sounds_parser.add_argument("size")

   # parser.add_argument(
   #     "command", 
   #     choices=[
   #         "get_bbc_categories",
   #         "get_bbc_sounds"
   #     ])

    args = parser.parse_args()

    cache_path = Path.home() / ".cache" / "terminal-effect-browser"
    bbc_db_path = cache_path / "database" / "bbc.db"

    logger = Logger()
 
    if args.command == "bbc_get_categories":
        bbc_categories = BBCCategories(logger, bbc_db_path)
        categories = bbc_categories.get_categories()
        for key, val in categories.items():
            category_name = key
            category_size = val
            print(f"{category_name} {category_size}")

    elif args.command == "bbc_get_sounds_data":
        bbc_sounds = BBCSounds(logger, bbc_db_path, args.category, args.size, headers)
        sounds_list = bbc_sounds.get_sounds()
        for val in sounds_list:
           print(f"{val}")

    elif args.command == "toggle_favourite":
        print(f"meow! oioioioioi {args.sound_id}")

    elif args.command == "is_favourite":
        print("1")

    elif args.command == "bbc_download_preview_sound":
        bbc_downloader = BBCSoundDownloader(logger, args.category, args.sound_id)
        bbc_downloader.download_preview_sound()
    
    else: 
        print(f"unknown command {args.command}")

if __name__ == "__main__":
    main()
