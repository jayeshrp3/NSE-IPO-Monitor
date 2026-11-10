"""Black-box fixtures that exercise a separately running application process."""

import os
import socket
import subprocess
import sys
import time
from collections.abc import Generator
from pathlib import Path

import httpx
import pytest
from playwright.sync_api import Browser, sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def database_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("ipo-harness") / "ipos.sqlite3"


@pytest.fixture
def base_url(
    database_path: Path,
    request: pytest.FixtureRequest,
) -> Generator[str, None, None]:
    output_path = database_path.with_suffix(".server.log")
    environment = os.environ.copy()
    environment["IPO_DATABASE_PATH"] = str(database_path)
    if hasattr(request, "param"):
        threshold = request.param
        if threshold is None:
            environment.pop("IPO_ALERT_THRESHOLD", None)
        else:
            environment["IPO_ALERT_THRESHOLD"] = str(threshold)
    else:
        environment["IPO_ALERT_THRESHOLD"] = "3"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"

    with output_path.open("w+", encoding="utf-8") as output:
        process = subprocess.Popen(
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
            cwd=PROJECT_ROOT,
            env=environment,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    output.seek(0)
                    raise RuntimeError(f"Application exited during startup:\n{output.read()}")
                try:
                    response = httpx.get(f"{url}/api/ipos", timeout=0.5)
                    if response.status_code == 200:
                        break
                except httpx.RequestError:
                    time.sleep(0.1)
            else:
                output.seek(0)
                raise RuntimeError(f"Application did not become ready:\n{output.read()}")
            yield url
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest.fixture
def client(base_url: str):
    with httpx.Client(base_url=base_url, timeout=5) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def browser() -> Browser:
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch()
        yield instance
        instance.close()
