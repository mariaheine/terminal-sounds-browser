#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

from src.logger import Logger
from src.bbc_categories import BBCCategories
from src.bbc_sounds_data import BBCSounds
from src.bbc_sound_downloader import BBCSoundDownloader
from src.constants import CACHE_DIR, SOUNDS_CACHE_DIR


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

    # bbc sounds subparser
    bbc_sounds_parser = subparsers.add_parser("bbc_get_sounds_data")
    bbc_sounds_parser.add_argument("category")
    bbc_sounds_parser.add_argument("category_size")

    log_debug = subparsers.add_parser("log_debug")
    log_debug.add_argument("message")

    args = parser.parse_args()

    logger = Logger()
 
    if args.command == "bbc_get_categories":
        bbc_categories = BBCCategories()
        categories = bbc_categories.get_categories()
        for key, val in categories.items():
            category_name = key
            category_size = val
            print(f"{category_name} {category_size}")

    elif args.command == "bbc_get_sounds_data":
        bbc_sounds = BBCSounds()
        sounds_list = bbc_sounds.get_printable_sounds_data(args.category, args.category_size)
        for val in sounds_list:
           print(val)

    elif args.command == "set_favourite":
        bbc_sounds = BBCSounds()
        value = bool(args.value)
        sound_id = str(args.sound_id)
        bbc_sounds.set_favourite(value, sound_id)

    elif args.command == "is_favourite":
        bbc_sounds = BBCSounds()
        is_favourite = bbc_sounds.is_favourite(args.sound_id)
        print(is_favourite)

    elif args.command == "bbc_download_preview_sound":
        bbc_downloader = BBCSoundDownloader(logger, args.category, args.sound_id)
        bbc_downloader.download_preview_sound()

    elif args.command == "log_debug":
        message = args.message
        logger.debug(message)
    
    else: 
        print(f"unknown command {args.command}")

if __name__ == "__main__":
    main()
