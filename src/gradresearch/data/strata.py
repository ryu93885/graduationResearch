"""Evaluation strata decided before any model is trained (R-25 / Q-08, adopted 2026-11-12).

``difficulty_group`` (one value per image):

* ``multi_unanimous``: multi-read image (read by Team 2 and Team 2a) whose final label
  equals the unanimous opinion of its readers.
* ``multi_difficult``: multi-read image whose readers disagreed on whether there is a
  Lung Opacity, or whose final label overturned the readers' unanimous opinion.
* ``single_low_prob``: not multi-read, and the highest probability among the readers' boxes
  is "low" (readers drew only low-probability opacities). A different kind of uncertainty
  (the reader's own doubt), so it is kept apart from ``multi_difficult``.
* ``single_other``: every other image.

``difficult_direction`` (only for ``multi_difficult``):

* ``final_negative_with_positive_read``: final label negative, at least one reader positive.
* ``final_positive_with_negative_read``: final label positive, at least one reader negative.

These strata are used to report results separately; no image is removed from training or
from the main evaluation because of them.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .annotations import OPACITY, PROB_ORDER

GROUPS = ("multi_unanimous", "multi_difficult", "single_low_prob", "single_other")
DIRECTIONS = ("final_negative_with_positive_read", "final_positive_with_negative_read")


def difficulty_strata(images: pd.DataFrame, reads: pd.DataFrame) -> pd.DataFrame:
    """Return ``image_id, n_reads, n_positive_votes, difficulty_group, difficult_direction``."""
    r = reads[reads["reader_class"].notna()].copy()
    r["positive"] = r["reader_class"].eq(OPACITY)
    r["prob_rank"] = r["max_probability"].map(PROB_ORDER)
    g = r.groupby("image_id")
    votes = pd.DataFrame(
        {
            "n_reads": g.size(),
            "n_positive_votes": g["positive"].sum().astype(int),
            "max_prob_rank": g["prob_rank"].max(),
        }
    )
    df = images[["image_id", "multi_read", "target", "has_final_label"]].join(votes, on="image_id")
    df["n_reads"] = df["n_reads"].fillna(0).astype(int)
    df["n_positive_votes"] = df["n_positive_votes"].fillna(0).astype(int)

    all_neg = (df["n_positive_votes"] == 0).to_numpy()
    all_pos = ((df["n_positive_votes"] == df["n_reads"]) & (df["n_reads"] > 0)).to_numpy()
    # pandas nullable integers (NA for images without a final label) -> float with NaN
    target = pd.to_numeric(df["target"], errors="coerce").astype(float).to_numpy()
    unanimous_agrees = (all_neg & (target == 0)) | (all_pos & (target == 1))
    low_only = (df["max_prob_rank"].astype(float) == PROB_ORDER["low"]).to_numpy()

    group = np.where(
        df["multi_read"].astype(bool).to_numpy(),
        np.where(unanimous_agrees, "multi_unanimous", "multi_difficult"),
        np.where(low_only, "single_low_prob", "single_other"),
    )
    df["difficulty_group"] = group
    direction = np.where(
        (group == "multi_difficult") & (target == 0),
        DIRECTIONS[0],
        np.where((group == "multi_difficult") & (target == 1), DIRECTIONS[1], ""),
    )
    df["difficult_direction"] = direction
    # Images without a final label are excluded from analysis (R-23); keep their group for reference.
    return df[["image_id", "n_reads", "n_positive_votes", "difficulty_group", "difficult_direction"]]
