"""Read pixel data of the RSNA images (straight from the ZIP or from extracted files)."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Union

import numpy as np
import pydicom


def read_pixels(source: Union[str, Path], member: str | None = None) -> np.ndarray:
    """Return the image as a ``uint8`` array (1024x1024, MONOCHROME2: 0 = black).

    ``source`` is either a ``.dcm`` file, or the image ZIP together with ``member`` (the
    ``zip_member`` column of ``images.csv``). Decoding needs Pillow (JPEG Baseline).
    """
    source = Path(source)
    if source.suffix.lower() == ".zip":
        if member is None:
            raise ValueError("member is required when reading from a ZIP file")
        with zipfile.ZipFile(source) as z, z.open(member) as f:
            ds = pydicom.dcmread(f)
            arr = ds.pixel_array
    else:
        ds = pydicom.dcmread(source)
        arr = ds.pixel_array
    if getattr(ds, "PhotometricInterpretation", "MONOCHROME2") == "MONOCHROME1":
        arr = arr.max() - arr
    return np.asarray(arr)
