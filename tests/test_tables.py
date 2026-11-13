import json

import pandas as pd
import pytest

from gradresearch.data.mapping import load_mapping
from gradresearch.data.sources import SOURCES
from gradresearch.data.strata import difficulty_strata
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
    # S3: Team 1 negative, Team 2 / 2a positive, final positive -> readers disagreed
    assert images.loc["img-3", "difficulty_group"] == "multi_difficult"
    assert images.loc["img-3", "difficult_direction"] == "final_positive_with_negative_read"
    assert images.loc["img-1", "difficulty_group"] == "single_other"
    assert not images.loc["img-4", "analysis_included"]
    assert (processed / "dicom_headers.csv").exists()

    loaded = load_tables(processed)
    assert len(loaded["images"]) == 4


# ---------------------------------------------------------------- strata
def _reads(rows):
    return pd.DataFrame(rows, columns=["image_id", "reader_class", "max_probability"])


def test_difficulty_strata_groups_and_directions():
    images = pd.DataFrame(
        {
            "image_id": ["u_neg", "u_pos", "split_pos", "split_neg", "overturned", "low", "single", "nolabel"],
            "multi_read": [True, True, True, True, True, False, False, True],
            "target": pd.array([0, 1, 1, 0, 0, 0, 1, None], dtype="Int64"),
            "has_final_label": [True] * 7 + [False],
        }
    )
    O, N, Z = "Lung Opacity", "No Lung Opacity / Not Normal", "Normal"
    reads = _reads(
        [
            ("u_neg", Z, None), ("u_neg", N, None), ("u_neg", Z, None),
            ("u_pos", O, "high"), ("u_pos", O, "medium"), ("u_pos", O, "medium"),
            ("split_pos", O, "medium"), ("split_pos", O, "low"), ("split_pos", N, None),
            ("split_neg", O, "low"), ("split_neg", N, None), ("split_neg", Z, None),
            ("overturned", O, "low"), ("overturned", O, "low"), ("overturned", O, "medium"),
            ("low", O, "low"),
            ("single", O, "high"),
            ("nolabel", O, "low"),
        ]
    )
    s = difficulty_strata(images, reads).set_index("image_id")
    assert s.loc["u_neg", "difficulty_group"] == "multi_unanimous"
    assert s.loc["u_pos", "difficulty_group"] == "multi_unanimous"
    assert s.loc["split_pos", "difficulty_group"] == "multi_difficult"
    assert s.loc["split_pos", "difficult_direction"] == "final_positive_with_negative_read"
    assert s.loc["split_neg", "difficult_direction"] == "final_negative_with_positive_read"
    assert s.loc["overturned", "difficulty_group"] == "multi_difficult"  # unanimous positive, final negative
    assert s.loc["overturned", "difficult_direction"] == "final_negative_with_positive_read"
    assert s.loc["low", "difficulty_group"] == "single_low_prob"
    assert s.loc["single", "difficulty_group"] == "single_other"
    assert s.loc["split_pos", "n_positive_votes"] == 2 and s.loc["split_pos", "n_reads"] == 3
