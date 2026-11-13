"""Patient-level K-fold cross-validation splits (R-03, R-26 / Q-09, adopted 2026-11-12).

* The unit is the NIH patient: all images of a patient go to the same fold, so no patient
  appears in both training and evaluation.
* Folds are balanced greedily, largest patients first, over the strata that matter for
  evaluation: final class x ``difficulty_group`` x view position (and the number of images).
* The order of patients with the same size is decided by ``random.Random(seed).random()``,
  whose sequence Python guarantees across versions, so Colab and the local PC produce the
  same folds. ``fingerprint`` gives a short hash of the assignment to compare them.
* Roles in run ``k`` (rotation): test = fold k, validation = fold (k+1) mod K,
  training = the other K-2 folds. With K = 5 this is 60% / 20% / 20% of the patients.
"""

from __future__ import annotations

import hashlib
import random
from typing import Sequence

import numpy as np
import pandas as pd

DEFAULT_KEYS = ("final_class", "difficulty_group", "view")


def _strata_key(images: pd.DataFrame, keys: Sequence[str]) -> pd.Series:
    cols = [c for c in keys if c in images.columns]
    return images[cols].astype(str).agg("|".join, axis=1) if cols else pd.Series("all", index=images.index)


def make_patient_folds(
    images: pd.DataFrame,
    n_folds: int = 5,
    seed: int = 42,
    keys: Sequence[str] = DEFAULT_KEYS,
    patient_col: str = "nih_patient_id",
) -> pd.DataFrame:
    """Assign every image to a fold. Balancing uses the analysis set only (``analysis_included``).

    Returns ``image_id, patient_col, fold``.
    """
    if n_folds < 3:
        raise ValueError("n_folds must be at least 3 (one fold each for test and validation)")
    included = images["analysis_included"] if "analysis_included" in images else pd.Series(True, index=images.index)
    lab = images[included.astype(bool)]
    strata = _strata_key(lab, keys)
    cats = sorted(strata.unique())
    cat_idx = {c: i for i, c in enumerate(cats)}

    # counts per patient x category (plus total images as an extra column)
    per = pd.crosstab(lab[patient_col], strata.map(cat_idx)).reindex(columns=range(len(cats)), fill_value=0)
    all_patients = sorted(images[patient_col].unique())
    per = per.reindex(all_patients, fill_value=0)
    counts = per.to_numpy(dtype=float)
    sizes = counts.sum(axis=1)

    rng = random.Random(seed)
    tiebreak = [rng.random() for _ in all_patients]
    order = sorted(range(len(all_patients)), key=lambda i: (-sizes[i], tiebreak[i]))

    totals = counts.sum(axis=0)
    totals[totals == 0] = 1.0
    total_images = max(sizes.sum(), 1.0)
    fold_counts = np.zeros((n_folds, counts.shape[1]))
    fold_sizes = np.zeros(n_folds)
    assignment = np.empty(len(all_patients), dtype=int)

    for i in order:
        best, best_cost = 0, None
        for f in range(n_folds):
            fc = fold_counts.copy()
            fc[f] += counts[i]
            fs = fold_sizes.copy()
            fs[f] += sizes[i]
            # spread of each category's share across folds, plus spread of fold sizes
            cost = float((fc / totals).std(axis=0).sum() + (fs / total_images).std() * len(cats))
            if best_cost is None or cost < best_cost - 1e-12 or (abs(cost - best_cost) <= 1e-12 and fold_sizes[f] < fold_sizes[best]):
                best, best_cost = f, cost
        assignment[i] = best
        fold_counts[best] += counts[i]
        fold_sizes[best] += sizes[i]

    fold_of = dict(zip(all_patients, assignment))
    out = images[["image_id", patient_col]].copy()
    out["fold"] = out[patient_col].map(fold_of).astype(int)
    return out


def fold_roles(run: int, n_folds: int) -> dict[str, list[int]]:
    """Folds used for test / validation / training in run ``run`` (rotation)."""
    if not 0 <= run < n_folds:
        raise ValueError(f"run must be in 0..{n_folds - 1}")
    test, val = run, (run + 1) % n_folds
    return {"test": [test], "val": [val], "train": [f for f in range(n_folds) if f not in (test, val)]}


def assign_roles(folds: pd.DataFrame, run: int, n_folds: int) -> pd.Series:
    roles = fold_roles(run, n_folds)
    role_of = {f: role for role, fs in roles.items() for f in fs}
    return folds["fold"].map(role_of)


def fingerprint(folds: pd.DataFrame) -> str:
    """Short SHA-256 of the sorted ``image_id:fold`` pairs (to compare environments)."""
    lines = sorted(f"{i}:{f}" for i, f in zip(folds["image_id"], folds["fold"]))
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()[:16]


def balance_table(images: pd.DataFrame, folds: pd.DataFrame) -> pd.DataFrame:
    """Per-fold counts of patients, images and the evaluation strata (analysis set only)."""
    df = images.merge(folds[["image_id", "fold"]], on="image_id")
    df = df[df["analysis_included"].astype(bool)] if "analysis_included" in df else df
    g = df.groupby("fold")
    t = pd.DataFrame(
        {
            "patients": g["nih_patient_id"].nunique(),
            "images": g.size(),
            "positives": g["target"].sum().astype(int),
            "positive_rate": g["target"].mean(),
        }
    )
    if "final_class" in df:
        t = t.join(pd.crosstab(df["fold"], df["final_class"]))
    if "view" in df:
        t["AP_share"] = g["view"].apply(lambda s: (s == "AP").mean())
    if "difficulty_group" in df:
        t = t.join(pd.crosstab(df["fold"], df["difficulty_group"]))
    if "difficult_direction" in df:
        d = df[df["difficult_direction"].fillna("") != ""]
        t = t.join(pd.crosstab(d["fold"], d["difficult_direction"])).fillna(0)
    return t


def balance_summary(table: pd.DataFrame) -> pd.DataFrame:
    """For each column: mean over folds, min, max and the largest relative deviation from the mean."""
    rows = []
    for c in table.columns:
        v = table[c].astype(float)
        mean = v.mean()
        rows.append(
            {
                "column": c,
                "mean": mean,
                "min": v.min(),
                "max": v.max(),
                "max_rel_dev": float((v - mean).abs().max() / mean) if mean else 0.0,
            }
        )
    return pd.DataFrame(rows).set_index("column")
