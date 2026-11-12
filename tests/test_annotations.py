import pandas as pd
import pytest

from gradresearch.data import annotations as A

from .conftest import make_project


def test_parse_label_name_strips_and_reads_probability():
    assert A.parse_label_name("Lung Opacity (Med Prob) ") == ("Lung Opacity", "medium")
    assert A.parse_label_name("Lung Opacity (High Prob)") == ("Lung Opacity", "high")
    assert A.parse_label_name("No Lung Opacity / Not Normal") == ("No Lung Opacity / Not Normal", None)


def test_final_labels_and_boxes():
    ann = A.annotation_table(make_project())
    images, boxes = A.final_labels(ann)
    by = images.set_index("study_uid")
    assert by.loc["S1", "final_class"] == A.OPACITY and by.loc["S1", "n_boxes"] == 2
    assert by.loc["S2", "final_class"] == A.NORMAL and by.loc["S2", "target"] == 0
    assert "S4" not in by.index  # no Calculated label
    assert len(boxes) == 3
    assert boxes[boxes.study_uid == "S1"]["box_index"].tolist() == [0, 1]


def test_conflicting_final_labels_raise():
    p = make_project()
    p["datasets"][0]["annotations"].append(
        {"id": "Z", "StudyInstanceUID": "S2", "SOPInstanceUID": "S2.sop", "labelId": "CN", "createdById": "CALC", "data": None}
    )
    with pytest.raises(ValueError, match="more than one final class"):
        A.final_labels(A.annotation_table(p))


def test_reader_reads_and_summary():
    ann = A.annotation_table(make_project())
    reads = A.reader_reads(ann)
    s3 = reads[reads.study_uid == "S3"].set_index("group")
    assert s3.loc["Team 1", "reader_class"] == A.NOT_NORMAL
    assert s3.loc["Team 2", "max_probability"] == "low"
    assert s3.loc["Team 2a", "reader_class"] == A.OPACITY
    s1 = reads[reads.study_uid == "S1"].iloc[0]
    assert s1["max_probability"] == "high" and s1["n_boxes"] == 2
    s4 = reads[reads.study_uid == "S4"].iloc[0]
    assert pd.isna(s4["reader_class"]) and s4["excluded"]

    summary = A.reader_summary(ann, reads).set_index("study_uid")
    assert summary.loc["S3", "multi_read"] and summary.loc["S3", "n_readers"] == 3
    assert summary.loc["S3", "n_positive_reads"] == 2 and summary.loc["S3", "adjudicated"]
    assert not summary.loc["S1", "multi_read"] and summary.loc["S1", "n_readers"] == 1
