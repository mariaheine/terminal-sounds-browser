#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

from src.backend.common.logger import Logger
from src.backend.constants import CACHE_DIR, SOUNDS_CACHE_DIR
from .bbc_categories import BBCCategories
from .bbc_sounds_data import BBCSounds
from .bbc_sound_downloader import BBCSoundDownloader


def main():
    parser = argparse.ArgumentParser(description="Sound Effect Browser")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # TODO make notes on python args parsers
    # bbc categories subparser
    bbc_categories_parser = subparsers.add_parser("bbc_get_categories")

    set_favourite_parser = subparsers.add_parser("set_favourite")
    set_favourite_parser.add_argument("value")
    set_favourite_parser.add_argument("sound_id")

    is_favourite_parser = subparsers.add_parser("is_favourite")
    is_favourite_parser.add_argument("sound_id")

    bbc_download_preview_parser = subparsers.add_parser("bbc_download_preview_sound")
    bbc_download_preview_parser.add_argument("sound_id")
    bbc_download_preview_parser.add_argument("category")

    bbc_sounds_parser = subparsers.add_parser("bbc_get_sounds_data")
    bbc_sounds_parser.add_argument("category")
    bbc_sounds_parser.add_argument("category_size")

    set_was_listened_parser = subparsers.add_parser("set_was_listened")
    set_was_listened_parser.add_argument("sound_id")

    get_preview_size_parser = subparsers.add_parser("get_preview_size")
    get_preview_size_parser.add_argument("sound_id")

    args = parser.parse_args()

    logger = Logger()
 
    if args.command == "bbc_get_categories":
        bbc_categories = BBCCategories()
        categories = bbc_categories.get_categories()
        for key, val in categories.items():
            # TODO move formatting into get categories
            category_name = key
            category_size = val
            print(f"{category_name} {category_size}")

    elif args.command == "bbc_get_sounds_data":
        bbc_sounds = BBCSounds()
        sounds_list = bbc_sounds.get_printable_sounds_data(args.category, args.category_size)
        for val in sounds_list[:10]:
            logger.debug(val)
        for val in sounds_list:
           print(val)

    elif args.command == "set_favourite":
        bbc_sounds = BBCSounds()
        value = bool(args.value)
        sound_id = str(args.sound_id)
        bbc_sounds.set_favourite(value, sound_id)

    elif args.command == "is_favourite":
        bbc_sounds = BBCSounds()
        sound_id = str(args.sound_id)
        is_favourite = bbc_sounds.is_favourite(sound_id)
        print(is_favourite)

    elif args.command == "bbc_download_preview_sound":
        bbc_downloader = BBCSoundDownloader()
        bbc_downloader.download_preview_sound(args.category, args.sound_id)

    elif args.command == "set_was_listened":
        bbc_sounds = BBCSounds()
        sound_id = str(args.sound_id)
        logger.debug(f"set was listened for {sound_id}")

    elif args.command == "get_preview_size":
        bbc_sounds = BBCSounds()
        size = bbc_sounds.get_preview_size(str(args.sound_id))
        print(size)

    else: 
        print(f"unknown command {args.command}")

if __name__ == "__main__":
    main()
