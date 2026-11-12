"""Files offered on the official RSNA distribution page.

Page: https://www.rsna.org/education/ai-resources-and-training/ai-image-challenge/RSNA-Pneumonia-Detection-Challenge-2018

Sizes were read from the server (Content-Length) on 2026-11-12. SHA-256 values were
computed from files downloaded on 2026-11-12; ``None`` means not yet recorded, in which
case only the size is checked and the computed hash is written to the manifest.

What each file contains (checked on 2026-11-12):

* ``annotations_full``: MD.ai project "ChestX-ray14 subset: Pneumonia" with all
  30,000 images. Holds every reader's labels (Team 1 = single readers, Team 2 /
  Team 2a = the multi-read cohort, Adjudication) with probability grades, and the
  final labels in the "Calculated" group (29,684 images).
* ``images_full``: the 30,000 DICOM images referenced by ``annotations_full``.
* ``mapping``: links each RSNA image to its NIH ChestX-ray14 file name (and thus the
  NIH patient ID), with the NIH labels used when the 30,000 images were selected.
* ``annotations_stage1``: MD.ai project for Kaggle stage 1 train (25,684 images,
  binary labels only). Used to mark which images were in Kaggle stage 1 train.
* ``images_stage1``: the 25,684 images of Kaggle stage 1 train. They are a subset of
  ``images_full`` and are not needed for this study.

Note: the page labels the stage 1 files "initial" and the full files "used in the
Pneumonia Challenge" (file names ``*-original_2018`` and ``*-adjudicated-kaggle_2018``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

BASE_URL = "https://s3.amazonaws.com/east1.public.rsna.org/AI/2018"


@dataclass(frozen=True)
class SourceFile:
    key: str
    filename: str
    size: int
    sha256: Optional[str]
    description: str
    default: bool  # downloaded unless explicitly excluded

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self.filename}"


SOURCES: dict[str, SourceFile] = {
    s.key: s
    for s in [
        SourceFile(
            key="annotations_full",
            filename="pneumonia-challenge-annotations-adjudicated-kaggle_2018.json",
            size=52_003_071,
            sha256="f8f5c54bae158fc0e2f019af979471803151a5922463ff3a378d7734e01b18fb",
            description="All readers' annotations and final labels for 30,000 images",
            default=True,
        ),
        SourceFile(
            key="mapping",
            filename="pneumonia-challenge-dataset-mappings_2018.json",
            size=17_587_143,
            sha256="803ce79e3bc9c66d3631738e91e62e1175730e98ad1415e8dc4d6292ba10bf27",
            description="Mapping from RSNA images to NIH ChestX-ray14 images",
            default=True,
        ),
        SourceFile(
            key="annotations_stage1",
            filename="pneumonia-challenge-annotations-original_2018.json",
            size=19_556_559,
            sha256="5fbfa5a70c9303460858deb476acf2af41ab98a9db24d5c77c3c34d7372c9f45",
            description="Kaggle stage 1 train annotations (25,684 images)",
            default=True,
        ),
        SourceFile(
            key="images_full",
            filename="pneumonia-challenge-dataset-adjudicated-kaggle_2018.zip",
            size=3_978_753_654,
            sha256="96b97d81eb042c6513196e01079a060a980d5e62502c3266527dd9c0b2a63b50",
            description="30,000 DICOM images (about 4.0 GB)",
            default=True,
        ),
        SourceFile(
            key="images_stage1",
            filename="pneumonia-challenge-dataset-original_2018.zip",
            size=3_410_618_175,
            sha256=None,
            description="Kaggle stage 1 train images (subset of images_full, about 3.4 GB)",
            default=False,
        ),
    ]
}


def default_keys() -> list[str]:
    return [k for k, s in SOURCES.items() if s.default]
