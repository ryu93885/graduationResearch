"""The RSNA-to-NIH mapping file (``pneumonia-challenge-dataset-mappings_2018.json``).

Each of the 30,000 records links one RSNA image to its NIH ChestX-ray14 file:

* ``subset_img_id``: the RSNA image ID (the Kaggle ``patientId`` and the DICOM PatientID;
  despite the name it identifies an image, not a patient)
* ``img_id``: NIH file name ``<8-digit NIH patient ID>_<3-digit follow-up number>.png``
* ``orig_labels``: NIH labels (mined from radiology reports by NLP)
* ``subset_init_label``: the selection group used when the 30,000 images were drawn
  (checked on 2026-11-12: 1 = 15,000 images with NIH labels such as Infiltration,
  Consolidation or Pneumonia; 0 = 7,500 "No Finding"; 2 = 7,500 other findings)
* ``subset_group``: an undocumented grouping (0/1/2); kept as is
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

SELECTION_GROUPS = {1: "pneumonia_related", 0: "no_finding", 2: "other_finding"}
_NIH = re.compile(r"^(?P<patient>\d{8})_(?P<followup>\d{3})\.png$")


def load_mapping(path: Path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as f:
        records = json.load(f)
    rows = []
    for r in records:
        m = _NIH.match(r["img_id"])
        if not m:
            raise ValueError(f"unexpected NIH file name: {r['img_id']}")
        rows.append(
            {
                "image_id": r["subset_img_id"],
                "study_uid": r["StudyInstanceUID"],
                "series_uid": r["SeriesInstanceUID"],
                "sop_uid": r["SOPInstanceUID"],
                "nih_image": r["img_id"],
                "nih_patient_id": int(m.group("patient")),
                "nih_followup": int(m.group("followup")),
                "nih_labels": "|".join(r["orig_labels"]),
                "selection_group": SELECTION_GROUPS.get(r["subset_init_label"], str(r["subset_init_label"])),
                "subset_group": r["subset_group"],
            }
        )
    df = pd.DataFrame(rows)
    for col in ("image_id", "study_uid", "sop_uid", "nih_image"):
        if df[col].duplicated().any():
            raise ValueError(f"duplicated {col} in the mapping file")
    return df
