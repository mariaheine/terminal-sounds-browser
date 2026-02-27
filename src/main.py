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

    # bbc categories subparser
    bbc_categories_parser = subparsers.add_parser("get_bbc_categories")

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
 
    logger.info
    
    if args.command == "get_bbc_categories":
        bbc_categories = BBCCategories(logger, bbc_db_path)
        categories = bbc_categories.get_categories()
        for key, val in categories.items():
            print(f"{key} {val}")

    elif args.command == "get_bbc_sounds":
        print(f"got cat: {args.category} {args.size}")
        bbc_sounds = BBCSounds(logger, bbc_db_path, args.category, args.size)
        sounds_list = bbc_sounds.get_sounds()
        for val in sounds_list:
           print(f"{val}")

        # for key, val in sounds_list.items():
        #     print(f"{key} {val}")
    
    else: 
        print(f"unknown command {args.command}")

if __name__ == "__main__":
    main()
