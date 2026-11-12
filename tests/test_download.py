"""Download tests against a local HTTP server that supports Range requests."""

from __future__ import annotations

import hashlib
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from gradresearch.data.download import DownloadError, download_file

PAYLOAD = bytes(range(256)) * 4000  # about 1 MB


class Handler(BaseHTTPRequestHandler):
    honour_range = True
    drop_first_n = 0  # close the connection mid-body for the first N requests
    requests_seen = 0

    def log_message(self, *args):  # keep test output quiet
        pass

    def do_GET(self):
        cls = type(self)
        cls.requests_seen += 1
        start = 0
        rng = self.headers.get("Range")
        if rng and cls.honour_range:
            start = int(rng.split("=")[1].split("-")[0])
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{len(PAYLOAD) - 1}/{len(PAYLOAD)}")
        else:
            self.send_response(200)
        body = PAYLOAD[start:]
        self.send_header("Content-Length", str(len(body)))
        self.send_header("ETag", '"test"')
        self.end_headers()
        if cls.requests_seen <= cls.drop_first_n:
            self.wfile.write(body[: len(body) // 3])
            self.wfile.flush()
            self.connection.shutdown(2)
            return
        self.wfile.write(body)


@pytest.fixture
def server():
    handler = type("H", (Handler,), {"honour_range": True, "drop_first_n": 0, "requests_seen": 0})
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield srv, handler
    srv.shutdown()


def _url(srv):
    return f"http://127.0.0.1:{srv.server_address[1]}/file.bin"


SHA = hashlib.sha256(PAYLOAD).hexdigest()


def test_fresh_download_verifies_size_and_hash(server, tmp_path):
    srv, _ = server
    rec = download_file(_url(srv), tmp_path / "f.bin", len(PAYLOAD), SHA, show_progress=False)
    assert (tmp_path / "f.bin").read_bytes() == PAYLOAD
    assert rec["sha256"] == SHA and rec["size"] == len(PAYLOAD) and rec["etag"] == '"test"'
    assert not (tmp_path / "f.bin.part").exists()


def test_resume_from_partial_file(server, tmp_path):
    srv, handler = server
    (tmp_path / "f.bin.part").write_bytes(PAYLOAD[:300_000])
    download_file(_url(srv), tmp_path / "f.bin", len(PAYLOAD), SHA, show_progress=False)
    assert (tmp_path / "f.bin").read_bytes() == PAYLOAD
    assert handler.requests_seen == 1


def test_server_ignoring_range_restarts_cleanly(server, tmp_path):
    srv, handler = server
    handler.honour_range = False
    (tmp_path / "f.bin.part").write_bytes(b"garbage" * 1000)
    download_file(_url(srv), tmp_path / "f.bin", len(PAYLOAD), SHA, show_progress=False)
    assert (tmp_path / "f.bin").read_bytes() == PAYLOAD


def test_dropped_connections_are_retried_and_resumed(server, tmp_path):
    srv, handler = server
    handler.drop_first_n = 2
    waits = []
    download_file(_url(srv), tmp_path / "f.bin", len(PAYLOAD), SHA, show_progress=False, sleep=waits.append)
    assert (tmp_path / "f.bin").read_bytes() == PAYLOAD
    assert waits == [2, 4]


def test_hash_mismatch_is_an_error(server, tmp_path):
    srv, _ = server
    with pytest.raises(DownloadError, match="SHA-256"):
        download_file(_url(srv), tmp_path / "f.bin", len(PAYLOAD), "0" * 64, show_progress=False)
    assert not (tmp_path / "f.bin").exists()


def test_size_mismatch_is_an_error(server, tmp_path):
    srv, _ = server
    with pytest.raises(DownloadError):
        download_file(_url(srv), tmp_path / "f.bin", len(PAYLOAD) + 10, None, show_progress=False,
                      sleep=lambda s: None, backoff=(0,))
