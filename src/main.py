#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

from src.logger import Logger
from src.bbc_categories import BBCCategories
from src.bbc_sounds import BBCSounds

def main():
    parser = argparse.ArgumentParser(description="Sound Effect Browser")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # TODO make notes on python args parsers
    # bbc categories subparser
    bbc_categories_parser = subparsers.add_parser("get_bbc_categories")

    toggle_favourite_parser = subparsers.add_parser("toggle_favourite")
    toggle_favourite_parser.add_argument("sound_id")

    is_favourite_parser = subparsers.add_parser("is_favourite")
    is_favourite_parser.add_argument("sound_id")

    # bbc sounds subparser
    bbc_sounds_parser = subparsers.add_parser("get_bbc_sounds")
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

    logger = Logger(cache_path)
 
    if args.command == "get_bbc_categories":
        bbc_categories = BBCCategories(logger, bbc_db_path)
        categories = bbc_categories.get_categories()
        for key, val in categories.items():
            print(f"{key} {val}")

    elif args.command == "get_bbc_sounds":
        bbc_sounds = BBCSounds(logger, bbc_db_path, args.category, args.size)
        sounds_list = bbc_sounds.get_sounds()
        for val in sounds_list:
           print(f"{val}")

    elif args.command == "toggle_favourite":
        print(f"meow! oioioioioi {args.sound_id}")

    elif args.command == "is_favourite":
        print("1")
    
    else: 
        print(f"unknown command {args.command}")

if __name__ == "__main__":
    main()
