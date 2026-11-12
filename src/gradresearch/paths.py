"""Where data and outputs live, for both Google Colab and a local GPU PC.

Resolution order for the data directory:
1. the ``GR_DATA_DIR`` environment variable, if set;
2. on Colab, ``/content/drive/MyDrive/graduationResearch/data`` when Google Drive is
   mounted (so downloads survive the session), otherwise ``/content/data``;
3. on a local PC, ``<repository>/data``.

Layout under the data directory::

    raw/        files downloaded from the official RSNA page (+ MANIFEST.json)
    processed/  tables built from the raw files (CSV)

Experiment outputs go to ``GR_OUTPUT_DIR`` or ``<data directory>/../outputs``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COLAB_DRIVE_ROOT = Path("/content/drive/MyDrive")


def is_colab() -> bool:
    """True when running inside Google Colab."""
    return "google.colab" in sys.modules or "COLAB_RELEASE_TAG" in os.environ


def data_dir() -> Path:
    env = os.environ.get("GR_DATA_DIR")
    if env:
        return Path(env).expanduser()
    if is_colab():
        if COLAB_DRIVE_ROOT.is_dir():
            return COLAB_DRIVE_ROOT / "graduationResearch" / "data"
        return Path("/content/data")
    return REPO_ROOT / "data"


def raw_dir() -> Path:
    return data_dir() / "raw"


def processed_dir() -> Path:
    return data_dir() / "processed"


def output_dir() -> Path:
    env = os.environ.get("GR_OUTPUT_DIR")
    if env:
        return Path(env).expanduser()
    return data_dir().parent / "outputs"


def describe() -> str:
    """One-line summary of the resolved paths, for logs and notebooks."""
    env = "Colab" if is_colab() else "local"
    return (
        f"environment={env} data_dir={data_dir()} "
        f"processed_dir={processed_dir()} output_dir={output_dir()}"
    )
