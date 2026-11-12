"""Download the official RSNA Pneumonia Detection Challenge 2018 files.

Examples
--------
List the files::

    python scripts/download_data.py --list

Download the default set (annotations, NIH mapping, 30,000 images; about 4.1 GB)::

    python scripts/download_data.py

Only the small JSON files (about 90 MB)::

    python scripts/download_data.py --keys annotations_full mapping annotations_stage1

Interrupted downloads resume from where they stopped when the command is run again.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from gradresearch import paths
from gradresearch.data.download import fetch
from gradresearch.data.sources import SOURCES, default_keys


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--keys", nargs="+", choices=sorted(SOURCES), help="files to download (default: the standard set)")
    p.add_argument("--data-dir", type=Path, help="data directory (default: GR_DATA_DIR or the environment default)")
    p.add_argument("--verify", action="store_true", help="recompute SHA-256 of files that are already present")
    p.add_argument("--no-zip-test", action="store_true", help="skip the CRC test of downloaded ZIP files")
    p.add_argument("--list", action="store_true", help="list the available files and exit")
    args = p.parse_args(argv)

    if args.list:
        for key, s in SOURCES.items():
            mark = "*" if s.default else " "
            print(f"{mark} {key:20s} {s.size / 1e6:9.1f} MB  {s.description}")
        print("(* = downloaded by default)")
        return 0

    if args.data_dir:
        os.environ["GR_DATA_DIR"] = str(args.data_dir)
    raw = paths.raw_dir()
    print(paths.describe())
    keys = args.keys or default_keys()
    for key in keys:
        fetch(SOURCES[key], raw, verify_existing=args.verify, check_zip=not args.no_zip_test)
    print(f"done: {', '.join(keys)} -> {raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
