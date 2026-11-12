"""Parse the MD.ai JSON exports distributed by RSNA.

Structure of ``pneumonia-challenge-annotations-adjudicated-kaggle_2018.json``
(checked on 2026-11-12)::

    {"labelGroups": [{"name": <group>, "labels": [{"id", "name", "type", "annotationMode"}]}],
     "datasets": [{"studies": [{"StudyInstanceUID", ...}],          # 30,000 images
                   "annotations": [{"StudyInstanceUID", "SOPInstanceUID", "labelId",
                                    "createdById", "data": {"x", "y", "width", "height"} | None,
                                    "height", "width"}]}]}          # image size, not box size

Label groups used here:

* ``Team 1``: the single readers (six RSNA readers read about 5,000 images each).
* ``Team 2`` / ``Team 2a``: the additional readers of the multi-read cohort.
* ``Adjudication``: labels added while resolving disagreements.
* ``Calculated``: the final labels (Lung Opacity with boxes / No Lung Opacity / Not Normal /
  Normal) for 29,684 images.

Reader labels carry a probability grade, e.g. ``"Lung Opacity (Med Prob) "`` (some names
end with a space).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

FINAL_GROUP = "Calculated"
READER_GROUPS = ("Team 1", "Team 2", "Team 2a")
ADJUDICATION_GROUP = "Adjudication"

OPACITY = "Lung Opacity"
NOT_NORMAL = "No Lung Opacity / Not Normal"
NORMAL = "Normal"
CLASSES = (OPACITY, NOT_NORMAL, NORMAL)

_PROB = re.compile(r"^(?P<base>.*?)\s*\((?P<prob>High|Med|Low) Prob\)\s*$")
_PROB_NAMES = {"High": "high", "Med": "medium", "Low": "low"}
PROB_ORDER = {"low": 1, "medium": 2, "high": 3}


def load_project(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_label_name(name: str) -> tuple[str, Optional[str]]:
    """``"Lung Opacity (Med Prob) "`` -> ``("Lung Opacity", "medium")``."""
    name = name.strip()
    m = _PROB.match(name)
    if m:
        return m.group("base").strip(), _PROB_NAMES[m.group("prob")]
    return name, None


def label_table(project: dict) -> pd.DataFrame:
    rows = []
    for g in project["labelGroups"]:
        for lab in g["labels"]:
            base, prob = parse_label_name(lab["name"])
            rows.append(
                {
                    "label_id": lab["id"],
                    "group": g["name"].strip(),
                    "label": base,
                    "probability": prob,
                    "label_type": lab.get("type"),
                    "annotation_mode": lab.get("annotationMode"),
                }
            )
    return pd.DataFrame(rows)


def annotation_table(project: dict) -> pd.DataFrame:
    """One row per annotation, with its label group, reader and box (NaN when no box)."""
    labels = label_table(project).set_index("label_id")
    rows = []
    for ds in project["datasets"]:
        for a in ds["annotations"]:
            box = a.get("data") or {}
            rows.append(
                {
                    "annotation_id": a["id"],
                    "study_uid": a["StudyInstanceUID"],
                    "sop_uid": a.get("SOPInstanceUID"),
                    "label_id": a["labelId"],
                    "reader_id": a.get("createdById"),
                    "x": box.get("x", np.nan),
                    "y": box.get("y", np.nan),
                    "w": box.get("width", np.nan),
                    "h": box.get("height", np.nan),
                    "img_h": a.get("height"),
                    "img_w": a.get("width"),
                }
            )
    df = pd.DataFrame(rows)
    missing = set(df["label_id"]) - set(labels.index)
    if missing:
        raise ValueError(f"annotations refer to unknown label ids: {sorted(missing)[:5]}")
    df = df.join(labels[["group", "label", "probability"]], on="label_id")
    for c in ("x", "y", "w", "h"):
        df[c] = df[c].astype(float)
    return df


def study_uids(project: dict) -> list[str]:
    return [s["StudyInstanceUID"] for ds in project["datasets"] for s in ds["studies"]]


def final_labels(ann: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Final (``Calculated``) labels.

    Returns ``(images, boxes)``:

    * images: ``study_uid, final_class, target, n_boxes`` (one row per labelled image)
    * boxes: ``study_uid, box_index, x, y, w, h`` (one row per final Lung Opacity box)
    """
    calc = ann[ann["group"] == FINAL_GROUP]
    unknown = set(calc["label"]) - set(CLASSES)
    if unknown:
        raise ValueError(f"unexpected final labels: {unknown}")
    per_study = calc.groupby("study_uid")["label"].agg(lambda s: sorted(set(s)))
    conflicting = per_study[per_study.map(len) > 1]
    if len(conflicting):
        raise ValueError(f"{len(conflicting)} images have more than one final class, e.g. {conflicting.index[0]}")
    images = per_study.map(lambda v: v[0]).rename("final_class").reset_index()
    images["target"] = (images["final_class"] == OPACITY).astype(int)

    boxes = calc[calc["label"] == OPACITY][["study_uid", "x", "y", "w", "h"]].copy()
    if boxes[["x", "y", "w", "h"]].isna().any().any():
        raise ValueError("a final Lung Opacity annotation has no box")
    boxes = boxes.sort_values(["study_uid", "x", "y"]).reset_index(drop=True)
    boxes.insert(1, "box_index", boxes.groupby("study_uid").cumcount())
    n = boxes.groupby("study_uid").size().rename("n_boxes")
    images = images.join(n, on="study_uid")
    images["n_boxes"] = images["n_boxes"].fillna(0).astype(int)
    if ((images["target"] == 1) != (images["n_boxes"] > 0)).any():
        raise ValueError("final class and number of boxes disagree for some images")
    return images, boxes


def _reader_class(labels: pd.Series) -> Optional[str]:
    s = set(labels)
    if OPACITY in s:
        return OPACITY
    if NOT_NORMAL in s:
        return NOT_NORMAL
    if NORMAL in s:
        return NORMAL
    return None  # only Question / Exclude / flags


def reader_reads(ann: pd.DataFrame) -> pd.DataFrame:
    """One row per (image, reader group, reader): the class that reader gave the image.

    Columns: ``study_uid, group, reader_id, reader_class, max_probability, n_boxes,
    excluded, question``.
    """
    r = ann[ann["group"].isin(READER_GROUPS)].copy()
    r["is_box"] = r["label"].eq(OPACITY) & r["w"].notna()
    r["prob_rank"] = r["probability"].map(PROB_ORDER)
    g = r.groupby(["study_uid", "group", "reader_id"])
    out = pd.DataFrame(
        {
            "reader_class": g["label"].agg(_reader_class),
            "max_prob_rank": g["prob_rank"].max(),
            "n_boxes": g["is_box"].sum().astype(int),
            "excluded": g["label"].agg(lambda s: "Exclude" in set(s)),
            "question": g["label"].agg(lambda s: "Question" in set(s)),
        }
    ).reset_index()
    inv = {v: k for k, v in PROB_ORDER.items()}
    out["max_probability"] = out.pop("max_prob_rank").map(inv)
    return out


def reader_summary(ann: pd.DataFrame, reads: pd.DataFrame) -> pd.DataFrame:
    """Per image: how it was read.

    * ``n_readers``: distinct readers in Team 1 / Team 2 / Team 2a
    * ``multi_read``: read by both Team 2 and Team 2a (the multi-read cohort; 4,526 images,
      matching the 4,527 stated by RSNA)
    * ``adjudicated``: has labels from the Adjudication group
    * ``n_positive_reads``: readers who drew at least one Lung Opacity box
    """
    groups = reads.groupby("study_uid")["group"].agg(set)
    out = pd.DataFrame(
        {
            "n_readers": reads.groupby("study_uid")["reader_id"].nunique(),
            "multi_read": groups.map(lambda s: {"Team 2", "Team 2a"} <= s),
            "n_positive_reads": reads.assign(p=reads["reader_class"].eq(OPACITY)).groupby("study_uid")["p"].sum().astype(int),
            "any_reader_excluded": reads.groupby("study_uid")["excluded"].any(),
        }
    )
    adj = set(ann.loc[ann["group"] == ADJUDICATION_GROUP, "study_uid"])
    out["adjudicated"] = out.index.isin(adj)
    out.index.name = "study_uid"
    return out.reset_index()
