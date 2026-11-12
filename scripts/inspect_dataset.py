"""Write the dataset inspection report from the processed tables.

Run ``scripts/build_tables.py`` first. Output: ``<output dir>/dataset_inspection/``
(``report.md``, ``summary.json`` and one CSV per table).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from gradresearch import paths
from gradresearch.analysis.dataset_report import build_report
from gradresearch.data.download import load_manifest
from gradresearch.data.tables import load_tables


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-dir", type=Path, help="data directory (default: GR_DATA_DIR or the environment default)")
    p.add_argument("--out", type=Path, help="output directory (default: <output dir>/dataset_inspection)")
    args = p.parse_args(argv)
    if args.data_dir:
        os.environ["GR_DATA_DIR"] = str(args.data_dir)
    tables = load_tables(paths.processed_dir())
    if "images" not in tables:
        print("processed tables not found; run scripts/build_tables.py first", file=sys.stderr)
        return 1
    out = args.out or paths.output_dir() / "dataset_inspection"
    report = build_report(tables, load_manifest(paths.raw_dir()), out)
    print(f"report -> {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
