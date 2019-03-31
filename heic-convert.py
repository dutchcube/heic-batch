#!/usr/bin/env python3

import argparse
import subprocess
import os
import sys
from os.path import join, split, splitext, isdir, dirname, abspath

TIFIG_PATH = join(abspath(dirname(__file__)), 'tifig')

def dep_check():
    if not os.path.isfile(TIFIG_PATH):
        print("tifig not found at {}".format(TIFIG_PATH))
        print("Please download the binary at https://github.com/monostream/tifig/releases")
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="Convert HEIC images to jpg (recursively)")
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="Overwrite existing files instead of skipping"
    )
    parser.add_argument(
        "ROOT_FOLDER",
        help="Folder to start conversion"
    )
    parser.add_argument(
        "-q",
        "--quality",
        default=90,
        dest="quality",
        type=int,
        help="JPEG quality (default: 90)"
    )
    parser.add_argument(
        "--rm",
        dest="rm",
        action="store_true",
        help="Delete original HEIC file after conversion"
    )

    return parser.parse_args()

def try_rename(heic, output):
    """ Portrait mode pictures are actually JPG already """
    try:
        magic = subprocess.check_output(['file', heic]).decode('utf-8')
    except subprocess.CalledProcessError:
        return

    if 'JPEG image data' in magic:
        print(heic, "is actually a JPG file already. Renaming..")
        try:
            os.replace(heic, output)
        except OSError as err:
            print("Error renaming:", err)

def process_heic(heic, args):
    rel_input = heic.replace(args.ROOT_FOLDER, '').strip('/')
    basename = splitext(heic)[0]
    output = '.'.join([basename, 'jpg'])
    rel_output = output.replace(args.ROOT_FOLDER, '').strip('/')
    if os.path.isfile(output) and not args.force:
        print(rel_output, "already exists")
        return

    try:
        subprocess.check_output([TIFIG_PATH, '-q', str(args.quality), '-p', heic, output])
        print("Converted", rel_input, "to", rel_output)
    except subprocess.CalledProcessError as err:
        print("Error converting", rel_input, "-", err.stdout, err.stderr)
        try_rename(heic, output)

    if args.rm:
        try:
            os.unlink(heic)
            print("Removed", heic)
        except OSError as err:
            print("Error removing", heic, "-", err)


def main(args):
    if not isdir(args.ROOT_FOLDER):
        print("Root folder is not a directory")
        sys.exit(1)

    for root, __, files in os.walk(args.ROOT_FOLDER):
        for heic in (f for f in files if f.lower().endswith('.heic')):
            process_heic(join(root, heic), args)


if __name__ == '__main__':
    args = parse_args()
    dep_check()
    main(args)
