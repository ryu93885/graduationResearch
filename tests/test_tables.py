import json

import numpy as np
import pytest

from gradresearch.analysis.dataset_report import auc, build_report, fleiss_kappa, md_table
from gradresearch.data.mapping import load_mapping
from gradresearch.data.sources import SOURCES
from gradresearch.data.tables import build_tables, load_tables


def test_mapping_parses_nih_patient(raw_dir):
    m = load_mapping(raw_dir / SOURCES["mapping"].filename).set_index("image_id")
    assert m.loc["img-2", "nih_patient_id"] == 1 and m.loc["img-2", "nih_followup"] == 1
    assert m.loc["img-2", "selection_group"] == "no_finding"
    assert m.loc["img-1", "selection_group"] == "pneumonia_related"


def test_mapping_rejects_duplicates(tmp_path):
    rec = {"img_id": "00000001_000.png", "subset_img_id": "a", "subset_group": 0, "subset_init_label": 0, "orig_labels": [],
           "StudyInstanceUID": "S", "SeriesInstanceUID": "s", "SOPInstanceUID": "o"}
    p = tmp_path / "m.json"
    p.write_text(json.dumps([rec, dict(rec, img_id="00000001_001.png", SOPInstanceUID="o2")]))
    with pytest.raises(ValueError, match="duplicated"):
        load_mapping(p)


def test_build_tables_end_to_end(raw_dir, tmp_path):
    processed = tmp_path / "data" / "processed"
    t = build_tables(raw_dir, processed, with_dicom=True)
    images = t["images"].set_index("image_id")
    assert len(images) == 4
    assert images["dicom_found"].all() and images["dicom_uids_match"].all()
    assert images.loc["img-1", "view"] == "AP" and images.loc["img-1", "age"] == 45
    assert images.loc["img-3", "multi_read"] and not images.loc["img-1", "multi_read"]
    assert not images.loc["img-4", "has_final_label"]
    assert images.loc["img-1", "kaggle_stage1_train"] and not images.loc["img-3", "kaggle_stage1_train"]
    assert (processed / "dicom_headers.csv").exists()

    loaded = load_tables(processed)
    report = build_report(loaded, {}, tmp_path / "out", title_date="2026-01-01")
    text = report.read_text(encoding="utf-8")
    assert "作成日：2026-01-01" in text and "view_x_class" in text
    summary = json.loads((tmp_path / "out" / "summary.json").read_text(encoding="utf-8"))
    assert summary["positive_images"] == 2 and summary["patients"] == 3


def test_fleiss_kappa_known_values():
    assert fleiss_kappa(np.array([[3, 0], [0, 3], [3, 0]])) == pytest.approx(1.0)
    # Example from Fleiss (1971) as reproduced on Wikipedia: kappa = 0.210
    table = np.array([
        [0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1],
        [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7],
    ])
    assert fleiss_kappa(table) == pytest.approx(0.210, abs=1e-3)


def test_auc_simple_cases():
    assert auc([0.1, 0.4, 0.35, 0.8], [0, 0, 1, 1]) == pytest.approx(0.75)
    assert auc([1, 1, 0, 0], [1, 1, 0, 0]) == pytest.approx(1.0)
    assert auc([1, 1, 1, 1], [1, 0, 1, 0]) == pytest.approx(0.5)


def test_md_table_formats_integers_without_decimals():
    import pandas as pd

    text = md_table(pd.DataFrame({"v": [316.0, 0.5, 12345.0]}, index=["a", "b", "c"]))
    assert "| a | 316 |" in text and "| b | 0.500 |" in text and "12,345" in text
