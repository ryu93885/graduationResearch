"""Read DICOM headers (without pixel data) from the image ZIP or an extracted folder.

Reading straight from the ZIP avoids extracting 30,000 files, which is slow on Google
Drive. Checked on 2026-11-12 with sample files: 1024x1024, 8 bits, MONOCHROME2, pixel
data compressed as JPEG Baseline (lossy); PixelSpacing differs between images.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Iterable, Iterator, Optional

import pandas as pd
import pydicom

TAGS = [
    "PatientID",
    "PatientAge",
    "PatientSex",
    "ViewPosition",
    "Modality",
    "BodyPartExamined",
    "Rows",
    "Columns",
    "PixelSpacing",
    "BitsStored",
    "PhotometricInterpretation",
    "LossyImageCompression",
    "StudyInstanceUID",
    "SOPInstanceUID",
]
_DIGITS = re.compile(r"\d+")


def header_record(ds: pydicom.Dataset) -> dict:
    age_raw = str(getattr(ds, "PatientAge", "") or "")
    m = _DIGITS.search(age_raw)
    spacing = getattr(ds, "PixelSpacing", None)
    tsuid = getattr(getattr(ds, "file_meta", None), "TransferSyntaxUID", None)
    return {
        "image_id": str(getattr(ds, "PatientID", "")),
        "study_uid": str(getattr(ds, "StudyInstanceUID", "")),
        "sop_uid": str(getattr(ds, "SOPInstanceUID", "")),
        "age_raw": age_raw,
        "age": int(m.group()) if m else None,
        "sex": str(getattr(ds, "PatientSex", "") or ""),
        "view": str(getattr(ds, "ViewPosition", "") or ""),
        "modality": str(getattr(ds, "Modality", "") or ""),
        "body_part": str(getattr(ds, "BodyPartExamined", "") or ""),
        "rows": int(getattr(ds, "Rows", 0) or 0),
        "cols": int(getattr(ds, "Columns", 0) or 0),
        "pixel_spacing": round(float(spacing[0]), 6) if spacing else None,
        "bits_stored": int(getattr(ds, "BitsStored", 0) or 0),
        "photometric": str(getattr(ds, "PhotometricInterpretation", "") or ""),
        "transfer_syntax": tsuid.name if tsuid is not None else "",
    }


def _progress(it: Iterable, total: int, desc: str, show: bool):
    if not show:
        return it
    from tqdm.auto import tqdm

    return tqdm(it, total=total, desc=desc)


def iter_zip_headers(zip_path: Path, limit: Optional[int] = None, show_progress: bool = True) -> Iterator[dict]:
    with zipfile.ZipFile(zip_path) as z:
        members = [i for i in z.infolist() if i.filename.lower().endswith(".dcm")]
        if limit:
            members = members[:limit]
        for info in _progress(members, len(members), "DICOM headers", show_progress):
            with z.open(info) as f:
                ds = pydicom.dcmread(f, stop_before_pixels=True)
            rec = header_record(ds)
            rec["file"] = info.filename
            yield rec


def iter_dir_headers(root: Path, limit: Optional[int] = None, show_progress: bool = True) -> Iterator[dict]:
    files = sorted(Path(root).rglob("*.dcm"))
    if limit:
        files = files[:limit]
    for p in _progress(files, len(files), "DICOM headers", show_progress):
        rec = header_record(pydicom.dcmread(p, stop_before_pixels=True))
        rec["file"] = str(p.relative_to(root))
        yield rec


def scan_headers(source: Path, limit: Optional[int] = None, show_progress: bool = True) -> pd.DataFrame:
    """Header table for every DICOM file in ``source`` (a ZIP file or a folder)."""
    source = Path(source)
    it = iter_zip_headers if source.suffix.lower() == ".zip" else iter_dir_headers
    return pd.DataFrame(list(it(source, limit, show_progress)))
