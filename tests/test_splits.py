import numpy as np
import pandas as pd
import pytest

from gradresearch.analysis.split_report import build_split_report
from gradresearch.data.splits import (
    assign_roles,
    balance_summary,
    balance_table,
    fingerprint,
    fold_roles,
    make_patient_folds,
)
from gradresearch.data.strata import difficulty_strata


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


# ---------------------------------------------------------------- folds
def synthetic_images(n_patients=2000, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for p in range(n_patients):
        k = int(rng.choice([1, 1, 1, 2, 3, 5, 12, 40], p=[0.3, 0.2, 0.1, 0.15, 0.1, 0.1, 0.04, 0.01]))
        for j in range(k):
            pos = rng.random() < 0.24
            rows.append(
                {
                    "image_id": f"p{p}_{j}",
                    "nih_patient_id": p,
                    "target": int(pos),
                    "final_class": "Lung Opacity" if pos else rng.choice(["No Lung Opacity / Not Normal", "Normal"]),
                    "difficulty_group": rng.choice(["multi_difficult", "multi_unanimous", "single_low_prob", "single_other"], p=[0.06, 0.1, 0.06, 0.78]),
                    "difficult_direction": "",
                    "view": "AP" if rng.random() < (0.77 if pos else 0.36) else "PA",
                    "analysis_included": rng.random() > 0.01,
                }
            )
    return pd.DataFrame(rows)


def test_folds_keep_patients_together_and_are_balanced():
    images = synthetic_images()
    folds = make_patient_folds(images, n_folds=5, seed=1)
    assert len(folds) == len(images) and folds["fold"].between(0, 4).all()
    assert (folds.groupby("nih_patient_id")["fold"].nunique() == 1).all()
    table = balance_table(images, folds)
    summary = balance_summary(table)
    assert summary.loc["images", "max_rel_dev"] < 0.05
    assert (table["positive_rate"] - table["positive_rate"].mean()).abs().max() < 0.01


def test_folds_are_deterministic_for_a_seed():
    images = synthetic_images(500)
    a = make_patient_folds(images, seed=7)
    b = make_patient_folds(images.sample(frac=1, random_state=3), seed=7)  # row order must not matter
    assert fingerprint(a) == fingerprint(b)
    assert fingerprint(a) != fingerprint(make_patient_folds(images, seed=8))


def test_fold_roles_rotation():
    seen_test, seen_val = set(), set()
    for k in range(5):
        r = fold_roles(k, 5)
        assert len(r["train"]) == 3 and set(r["train"]).isdisjoint(r["test"] + r["val"])
        seen_test.update(r["test"])
        seen_val.update(r["val"])
    assert seen_test == seen_val == set(range(5))
    with pytest.raises(ValueError):
        make_patient_folds(synthetic_images(10), n_folds=2)


def test_assign_roles_and_report(tmp_path):
    images = synthetic_images(300)
    folds = make_patient_folds(images, n_folds=5)
    roles = assign_roles(folds, run=2, n_folds=5)
    assert set(roles.unique()) == {"train", "val", "test"}
    assert (folds.loc[roles == "test", "fold"] == 2).all()
    report = build_split_report(images, folds, 5, 42, tmp_path, date="2026-01-01")
    text = report.read_text(encoding="utf-8")
    assert "作成日：2026-01-01" in text and "偏りの判定" in text
