"""Build the processed tables (images / boxes / reader_reads / reader_boxes) from raw files.

Examples
--------
Full build, including a scan of the 30,000 DICOM headers inside the ZIP (a few minutes)::

    python scripts/build_tables.py

Annotations and mapping only (no image ZIP needed)::

    python scripts/build_tables.py --no-dicom
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from gradresearch import paths
from gradresearch.data.tables import build_tables


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", type=Path, help="data directory (default: GR_DATA_DIR or the environment default)")
    p.add_argument("--no-dicom", action="store_true", help="skip the DICOM header scan")
    p.add_argument("--rescan", action="store_true", help="scan DICOM headers again even if cached")
    p.add_argument("--dicom-limit", type=int, help="scan only the first N DICOM files (for a quick test)")
    args = p.parse_args(argv)
    if args.data_dir:
        os.environ["GR_DATA_DIR"] = str(args.data_dir)
    print(paths.describe())
    t = time.time()
    tables = build_tables(
        paths.raw_dir(),
        paths.processed_dir(),
        with_dicom=not args.no_dicom,
        rescan=args.rescan,
        dicom_limit=args.dicom_limit,
    )
    for name, df in tables.items():
        print(f"{name:14s} {len(df):7,d} rows -> {paths.processed_dir() / (name + '.csv')}")
    print(f"done in {time.time() - t:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
