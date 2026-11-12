"""Resumable, verified downloads of the official RSNA files.

* Large files are streamed to ``<name>.part`` and resumed with HTTP Range requests
  after an interruption (a dropped Wi-Fi connection or a Colab disconnect).
* Network errors are retried with exponential backoff (2, 4, 8, 16, 32 s).
* After the download the size is checked, the SHA-256 is computed and compared with
  the known value (when one is recorded), and the result is written to
  ``raw/MANIFEST.json`` together with the date, URL and library versions, for
  reproducibility.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import platform
import time
import zipfile
from pathlib import Path
from typing import Callable, Optional

import requests

from .sources import SourceFile

CHUNK = 8 * 1024 * 1024
BACKOFF = (2, 4, 8, 16, 32)


class DownloadError(RuntimeError):
    pass


def sha256_of(path: Path, chunk: int = CHUNK) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _progress(total: Optional[int], initial: int, desc: str):
    try:
        from tqdm.auto import tqdm
    except ImportError:  # pragma: no cover - tqdm is a dependency
        return None
    return tqdm(total=total, initial=initial, unit="B", unit_scale=True, unit_divisor=1024, desc=desc)


def _stream_once(session: requests.Session, url: str, part: Path, timeout: float, show_progress: bool) -> dict:
    """Download (or continue downloading) ``url`` into ``part``. Returns response headers."""
    have = part.stat().st_size if part.exists() else 0
    headers = {"Range": f"bytes={have}-"} if have else {}
    with session.get(url, headers=headers, stream=True, timeout=timeout) as r:
        if r.status_code == 416:  # nothing left to fetch: the part file is already complete
            return dict(r.headers)
        r.raise_for_status()
        if have and r.status_code != 206:  # server ignored the Range header: start over
            have = 0
        mode = "ab" if have else "wb"
        total = None
        if "Content-Length" in r.headers:
            total = have + int(r.headers["Content-Length"])
        bar = _progress(total, have, part.name.removesuffix(".part")) if show_progress else None
        try:
            with open(part, mode) as f:
                for block in r.iter_content(chunk_size=CHUNK):
                    if block:
                        f.write(block)
                        if bar is not None:
                            bar.update(len(block))
        finally:
            if bar is not None:
                bar.close()
        return dict(r.headers)


def download_file(
    url: str,
    dest: Path,
    expected_size: Optional[int] = None,
    expected_sha256: Optional[str] = None,
    *,
    session: Optional[requests.Session] = None,
    timeout: float = 60.0,
    backoff: tuple[float, ...] = BACKOFF,
    sleep: Callable[[float], None] = time.sleep,
    show_progress: bool = True,
) -> dict:
    """Download ``url`` to ``dest`` with resume and verification. Returns a manifest record."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    session = session or requests.Session()

    headers: dict = {}
    for attempt in range(len(backoff) + 1):
        try:
            headers = _stream_once(session, url, part, timeout, show_progress)
            have = part.stat().st_size
            if expected_size is not None and have < expected_size:
                raise DownloadError(f"connection ended early ({have} of {expected_size} bytes)")
            break
        except (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError, DownloadError) as e:
            if attempt == len(backoff):
                raise DownloadError(f"giving up on {url} after {attempt + 1} attempts: {e}") from e
            wait = backoff[attempt]
            print(f"[download] {dest.name}: {e}; retrying in {wait}s (attempt {attempt + 2})")
            sleep(wait)

    size = part.stat().st_size
    if expected_size is not None and size != expected_size:
        raise DownloadError(
            f"{dest.name}: size {size} does not match the expected {expected_size}. "
            f"Delete {part} and download again; if it keeps happening, the file on the server may have changed."
        )
    digest = sha256_of(part)
    if expected_sha256 is not None and digest != expected_sha256:
        raise DownloadError(
            f"{dest.name}: SHA-256 {digest} does not match the recorded {expected_sha256}. "
            f"The file may be corrupted or may have been updated on the server."
        )
    part.replace(dest)
    return _record(url, dest, size, digest, headers)


def _record(url: str, dest: Path, size: int, digest: str, headers: dict) -> dict:
    import pandas
    import pydicom

    return {
        "filename": dest.name,
        "url": url,
        "size": size,
        "sha256": digest,
        "etag": headers.get("ETag"),
        "last_modified": headers.get("Last-Modified"),
        "downloaded_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "requests": requests.__version__,
        "pandas": pandas.__version__,
        "pydicom": pydicom.__version__,
    }


def test_zip(path: Path) -> dict:
    """Check every member's CRC and count entries. Takes about a minute for 4 GB."""
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        infos = z.infolist()
    if bad is not None:
        raise DownloadError(f"{path.name}: corrupted member {bad}")
    files = [i for i in infos if not i.is_dir()]
    return {"zip_entries": len(files), "zip_uncompressed_bytes": sum(i.file_size for i in files)}


def load_manifest(raw: Path) -> dict:
    p = Path(raw) / "MANIFEST.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_manifest(raw: Path, manifest: dict) -> None:
    p = Path(raw) / "MANIFEST.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch(source: SourceFile, raw: Path, *, verify_existing: bool = False, check_zip: bool = True) -> dict:
    """Download one official file into ``raw`` unless a verified copy is already there."""
    raw = Path(raw)
    dest = raw / source.filename
    manifest = load_manifest(raw)
    if dest.exists() and dest.stat().st_size == source.size:
        if not verify_existing:
            print(f"[skip] {dest.name} already present ({source.size:,} bytes)")
            return manifest.get(dest.name, {"filename": dest.name, "size": source.size})
        digest = sha256_of(dest)
        known = source.sha256 or manifest.get(dest.name, {}).get("sha256")
        if known is None or digest == known:
            print(f"[ok] {dest.name} verified")
            return manifest.get(dest.name, {"filename": dest.name, "size": source.size, "sha256": digest})
        print(f"[warn] {dest.name} has an unexpected SHA-256; downloading again")
        dest.unlink()

    print(f"[download] {source.filename} ({source.size / 1e9:.2f} GB)" if source.size > 1e9 else f"[download] {source.filename}")
    record = download_file(source.url, dest, source.size, source.sha256)
    if check_zip and dest.suffix == ".zip":
        print(f"[check] testing every file in {dest.name} ...")
        record.update(test_zip(dest))
    manifest[dest.name] = record
    save_manifest(raw, manifest)
    return record
