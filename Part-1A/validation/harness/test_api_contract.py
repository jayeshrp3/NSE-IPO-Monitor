"""Public HTTP contract checks; application modules are intentionally not imported."""

import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest


def test_list_contract_and_static_assets(client):
    response = client.get("/api/ipos")
    assert response.status_code == 200
    assert response.json() == []

    stylesheet = client.get("/static/css/styles.css")
    script = client.get("/static/js/app.js")
    assert stylesheet.status_code == 200
    assert "text/css" in stylesheet.headers["content-type"]
    assert script.status_code == 200
    assert "javascript" in script.headers["content-type"]


def test_missing_record_and_request_validation_contract(client):
    assert client.get("/api/ipos/999999").status_code == 404

    response = client.post(
        "/api/ipos",
        json={
            "company_name": "Contract IPO",
            "opening_date": "2026-02-30",
            "closing_date": "2026-03-01",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"]


@pytest.mark.parametrize("threshold", ["not-an-integer", "-1"])
def test_invalid_alert_threshold_prevents_application_startup(tmp_path, threshold):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    environment = os.environ.copy()
    environment["IPO_DATABASE_PATH"] = str(tmp_path / "invalid-threshold.sqlite3")
    environment["IPO_ALERT_THRESHOLD"] = threshold
    project_root = Path(__file__).resolve().parents[2]
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=project_root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert process.returncode != 0
    assert "IPO_ALERT_THRESHOLD must be a non-negative integer" in (
        process.stdout + process.stderr
    )
