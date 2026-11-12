"""Synthetic stand-ins for the RSNA files, so tests run offline in seconds."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pydicom
import pytest
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

from gradresearch.data.sources import SOURCES

LABEL_GROUPS = [
    {"name": "Team 1", "labels": [
        {"id": "T1H", "name": "Lung Opacity (High Prob)", "type": "local", "annotationMode": "bbox"},
        {"id": "T1M", "name": "Lung Opacity (Med Prob) ", "type": "local", "annotationMode": "bbox"},
        {"id": "T1N", "name": "No Lung Opacity / Not Normal", "type": "global", "annotationMode": None},
        {"id": "T1O", "name": "Normal", "type": "global", "annotationMode": None},
        {"id": "T1X", "name": "Exclude", "type": "global", "annotationMode": None},
    ]},
    {"name": "Team 2", "labels": [
        {"id": "T2L", "name": "Lung Opacity (Low Prob) ", "type": "local", "annotationMode": "bbox"},
        {"id": "T2O", "name": "Normal", "type": "global", "annotationMode": None},
    ]},
    {"name": "Team 2a", "labels": [
        {"id": "T3M", "name": "Lung Opacity (Med Prob)", "type": "local", "annotationMode": "bbox"},
        {"id": "T3N", "name": "No Lung Opacity / Not Normal", "type": "global", "annotationMode": None},
    ]},
    {"name": "Adjudication", "labels": [
        {"id": "ADF", "name": "Flag", "type": "global", "annotationMode": None},
    ]},
    {"name": "Calculated", "labels": [
        {"id": "CO", "name": "Normal", "type": "global", "annotationMode": None},
        {"id": "CN", "name": "No Lung Opacity / Not Normal", "type": "global", "annotationMode": None},
        {"id": "CL", "name": "Lung Opacity", "type": "local", "annotationMode": "bbox"},
    ]},
]

# study -> (image_id, NIH file name, selection label)
STUDIES = {
    "S1": ("img-1", "00000001_000.png", 1),  # single read, positive with 2 boxes
    "S2": ("img-2", "00000001_001.png", 0),  # single read, normal
    "S3": ("img-3", "00000002_000.png", 2),  # multi read, positive (2 of 3 readers)
    "S4": ("img-4", "00000003_000.png", 1),  # excluded: no final label
}


def _ann(i, study, label, reader, box=None):
    return {
        "id": f"A{i}", "StudyInstanceUID": study, "SOPInstanceUID": f"{study}.sop", "labelId": label,
        "createdById": reader, "data": box, "height": 1024, "width": 1024,
    }


def make_project() -> dict:
    b = lambda x, y, w, h: {"x": x, "y": y, "width": w, "height": h}  # noqa: E731
    anns = [
        _ann(1, "S1", "T1M", "R1", b(100, 200, 150, 300)),
        _ann(2, "S1", "T1H", "R1", b(600, 250, 120, 280)),
        _ann(3, "S1", "CL", "CALC", b(100, 200, 150, 300)),
        _ann(4, "S1", "CL", "CALC", b(600, 250, 120, 280)),
        _ann(5, "S2", "T1O", "R2", None),
        _ann(6, "S2", "CO", "CALC", None),
        _ann(7, "S3", "T1N", "R1", None),
        _ann(8, "S3", "T2L", "R3", b(300, 300, 100, 100)),
        _ann(9, "S3", "T3M", "R4", b(310, 310, 80, 90)),
        _ann(10, "S3", "ADF", "ADJ", None),
        _ann(11, "S3", "CL", "CALC", b(310, 310, 80, 90)),
        _ann(12, "S4", "T1X", "R2", None),
    ]
    return {
        "name": "synthetic",
        "labelGroups": LABEL_GROUPS,
        "datasets": [{"studies": [{"StudyInstanceUID": s} for s in STUDIES], "annotations": anns}],
    }


def make_mapping() -> list[dict]:
    return [
        {
            "img_id": nih, "subset_img_id": img, "subset_group": 0, "subset_init_label": sel,
            "orig_labels": ["No Finding"] if sel == 0 else ["Infiltration"],
            "StudyInstanceUID": study, "SeriesInstanceUID": f"{study}.series", "SOPInstanceUID": f"{study}.sop",
            "studyId": "x", "seriesId": "x", "instanceId": "x",
        }
        for study, (img, nih, sel) in STUDIES.items()
    ]


def make_stage1() -> dict:
    return {
        "labelGroups": [{"name": "Default group", "labels": [{"id": "L", "name": "Lung Opacity", "type": "local", "annotationMode": "bbox"}]}],
        "datasets": [{"studies": [{"StudyInstanceUID": "S1"}, {"StudyInstanceUID": "S2"}], "annotations": []}],
    }


def dicom_bytes(image_id: str, study: str, view: str, age: str) -> bytes:
    meta = FileMetaDataset()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
    meta.MediaStorageSOPInstanceUID = f"{study}.sop"
    ds = Dataset()
    ds.file_meta = meta
    ds.PatientID, ds.PatientAge, ds.PatientSex, ds.ViewPosition = image_id, age, "M", view
    ds.Modality, ds.BodyPartExamined = "CR", "CHEST"
    ds.StudyInstanceUID, ds.SeriesInstanceUID, ds.SOPInstanceUID = study, f"{study}.series", f"{study}.sop"
    ds.SOPClassUID = meta.MediaStorageSOPClassUID
    ds.Rows = ds.Columns = 1024
    ds.PixelSpacing = [0.168, 0.168]
    ds.BitsStored, ds.BitsAllocated = 8, 8
    ds.PhotometricInterpretation = "MONOCHROME2"
    buf = io.BytesIO()
    if _pydicom3():
        pydicom.dcmwrite(buf, ds, enforce_file_format=True)
    else:  # pydicom 2.x
        ds.is_little_endian, ds.is_implicit_VR = True, False
        ds.save_as(buf, write_like_original=False)
    return buf.getvalue()


def _pydicom3() -> bool:
    return int(pydicom.__version__.split(".")[0]) >= 3


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / SOURCES["annotations_full"].filename).write_text(json.dumps(make_project()), encoding="utf-8")
    (raw / SOURCES["mapping"].filename).write_text(json.dumps(make_mapping()), encoding="utf-8")
    (raw / SOURCES["annotations_stage1"].filename).write_text(json.dumps(make_stage1()), encoding="utf-8")
    views = {"S1": "AP", "S2": "PA", "S3": "AP", "S4": "PA"}
    with zipfile.ZipFile(raw / SOURCES["images_full"].filename, "w", zipfile.ZIP_DEFLATED) as z:
        for study, (img, _, _) in STUDIES.items():
            z.writestr(f"root/{study}/{study}.series/{study}.sop.dcm", dicom_bytes(img, study, views[study], "045Y"))
    return raw
