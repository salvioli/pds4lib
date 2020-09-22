#!/usr/bin/env python3

from pds4lib.product import Collection
import sys
from pathlib import Path


def is_path_including_collections(path):
    collections = get_collections_in_path(path)
    return len(collections) > 0


def get_collections_in_path(path):
    path = Path(path)
    collections = list(path.rglob('collection*.xml'))
    return collections


def validate_input(argv):
    if len(argv) != 2 or argv[1] == '-h' or argv[1] == '--help':
        print_help(argv)
        exit(-1)
    else:
        path = Path(argv[1])
        if not path.exists():
            raise_invalid_path_error(argv)
        elif path.is_dir() and not is_path_including_collections(path):
            raise_invalid_path_error(argv)


def raise_invalid_path_error(argv):
    print(
        f'The provided argument {argv[1]} is not a valid file or directory, '
        f'please provide a valid PDS4 collection label or a directory that includes '
        f'one or more collections')
    print_help(argv)
    exit(-1)


def print_help(argv):
    print(f"Example usage: {argv[0]} <collection_label.xml>")


def update_collection(collection):
    collection = Collection(collection)
    print(f'updating collection {collection.path}')
    collection.update()


if __name__ == "__main__":
    validate_input(sys.argv)
    path = Path(sys.argv[1])

    if path.is_dir():
        for c in get_collections_in_path(path):
            update_collection(c)
    if path.is_file():
        update_collection(path)
