"""Build the tidy tables used by later steps from the raw RSNA files.

Outputs (CSV, in ``processed/``):

* ``images.csv``: one row per image (30,000): IDs, NIH patient ID, selection group,
  final class / target, number of boxes, how the image was read, Kaggle stage 1
  membership and DICOM header fields.
* ``boxes.csv``: final Lung Opacity boxes (x, y, w, h in pixels of the 1024x1024 image;
  x, y is the top-left corner).
* ``reader_reads.csv``: the class each reader gave each image (Team 1 / 2 / 2a).
* ``reader_boxes.csv``: every box drawn by a reader, with its probability grade.
* ``dicom_headers.csv``: the raw DICOM header scan (cached; rebuilt with ``rescan``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from . import annotations as A
from .dicom_meta import scan_headers
from .mapping import load_mapping
from .sources import SOURCES


def _raw_file(raw: Path, key: str) -> Path:
    return Path(raw) / SOURCES[key].filename


def build_tables(
    raw: Path,
    processed: Path,
    *,
    with_dicom: bool = True,
    rescan: bool = False,
    dicom_limit: Optional[int] = None,
) -> dict[str, pd.DataFrame]:
    raw, processed = Path(raw), Path(processed)
    processed.mkdir(parents=True, exist_ok=True)

    mapping = load_mapping(_raw_file(raw, "mapping"))
    project = A.load_project(_raw_file(raw, "annotations_full"))
    ann = A.annotation_table(project)
    final, boxes = A.final_labels(ann)
    reads = A.reader_reads(ann)
    summary = A.reader_summary(ann, reads)

    images = mapping.merge(final, on="study_uid", how="left", validate="one_to_one")
    images["has_final_label"] = images["final_class"].notna()
    images["target"] = images["target"].astype("Int64")
    images["n_boxes"] = images["n_boxes"].fillna(0).astype(int)
    images = images.merge(summary, on="study_uid", how="left", validate="one_to_one")
    for col in ("multi_read", "adjudicated", "any_reader_excluded"):
        images[col] = images[col].astype("boolean").fillna(False).astype(bool)
    images["n_readers"] = images["n_readers"].fillna(0).astype(int)
    images["n_positive_reads"] = images["n_positive_reads"].fillna(0).astype(int)

    stage1_path = _raw_file(raw, "annotations_stage1")
    if stage1_path.exists():
        stage1 = set(A.study_uids(A.load_project(stage1_path)))
        images["kaggle_stage1_train"] = images["study_uid"].isin(stage1)

    id_of_study = images.set_index("study_uid")["image_id"]
    boxes.insert(0, "image_id", boxes["study_uid"].map(id_of_study))
    reads.insert(0, "image_id", reads["study_uid"].map(id_of_study))
    reader_boxes = ann[ann["group"].isin(A.READER_GROUPS) & ann["w"].notna()][
        ["study_uid", "group", "reader_id", "probability", "x", "y", "w", "h"]
    ].copy()
    reader_boxes.insert(0, "image_id", reader_boxes["study_uid"].map(id_of_study))

    if with_dicom:
        headers_csv = processed / "dicom_headers.csv"
        if headers_csv.exists() and not rescan and dicom_limit is None:
            headers = pd.read_csv(headers_csv)
        else:
            zip_path = _raw_file(raw, "images_full")
            if not zip_path.exists():
                raise FileNotFoundError(f"{zip_path} not found; run scripts/download_data.py first or pass --no-dicom")
            headers = scan_headers(zip_path, limit=dicom_limit)
            if dicom_limit is None:
                headers.to_csv(headers_csv, index=False)
        h = headers.rename(columns={"study_uid": "dicom_study_uid", "sop_uid": "dicom_sop_uid", "file": "zip_member"})
        images = images.merge(h, on="image_id", how="left", validate="one_to_one")
        images["dicom_found"] = images["zip_member"].notna()
        images["dicom_uids_match"] = (images["dicom_study_uid"] == images["study_uid"]) & (
            images["dicom_sop_uid"] == images["sop_uid"]
        )
        images = images.drop(columns=["dicom_study_uid", "dicom_sop_uid"])

    tables = {
        "images": images,
        "boxes": boxes,
        "reader_reads": reads,
        "reader_boxes": reader_boxes,
    }
    for name, df in tables.items():
        df.to_csv(processed / f"{name}.csv", index=False)
    return tables


def load_tables(processed: Path) -> dict[str, pd.DataFrame]:
    processed = Path(processed)
    return {
        name: pd.read_csv(processed / f"{name}.csv")
        for name in ("images", "boxes", "reader_reads", "reader_boxes")
        if (processed / f"{name}.csv").exists()
    }
