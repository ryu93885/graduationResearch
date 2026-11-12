"""Make the patient-level cross-validation folds and check how balanced they are.

Run ``scripts/build_tables.py`` first (``images.csv`` must contain ``difficulty_group``).

Outputs
-------
* ``<data dir>/processed/splits/folds_k<K>_seed<S>.csv``: ``image_id, nih_patient_id, fold``
* ``<output dir>/splits/fold_balance.md`` (+ CSV): per-fold counts and the balance check
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

from gradresearch import paths
from gradresearch.analysis.split_report import build_split_report
from gradresearch.data.splits import fingerprint, make_patient_folds


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n-folds", type=int, default=5, help="number of folds (default: 5)")
    p.add_argument("--seed", type=int, default=42, help="seed for the order of equal-sized patients (default: 42)")
    p.add_argument("--data-dir", type=Path, help="data directory (default: GR_DATA_DIR or the environment default)")
    p.add_argument("--out", type=Path, help="report directory (default: <output dir>/splits)")
    args = p.parse_args(argv)
    if args.data_dir:
        os.environ["GR_DATA_DIR"] = str(args.data_dir)

    images_csv = paths.processed_dir() / "images.csv"
    if not images_csv.exists():
        print("images.csv not found; run scripts/build_tables.py first", file=sys.stderr)
        return 1
    images = pd.read_csv(images_csv)
    if "difficulty_group" not in images:
        print("images.csv has no difficulty_group column; run scripts/build_tables.py again", file=sys.stderr)
        return 1

    folds = make_patient_folds(images, n_folds=args.n_folds, seed=args.seed)
    split_dir = paths.processed_dir() / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    folds_csv = split_dir / f"folds_k{args.n_folds}_seed{args.seed}.csv"
    folds.to_csv(folds_csv, index=False)
    report = build_split_report(images, folds, args.n_folds, args.seed, args.out or paths.output_dir() / "splits")
    print(f"folds -> {folds_csv} (fingerprint {fingerprint(folds)})")
    print(f"report -> {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
