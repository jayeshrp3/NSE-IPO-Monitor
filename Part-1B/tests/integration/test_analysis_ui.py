from fastapi.testclient import TestClient

from app.main import create_app


def test_interface_and_analysis_route_are_available():
    with TestClient(create_app()) as client:
        page = client.get("/")
        static = client.get("/static/app.js")

    assert page.status_code == 200
    assert static.status_code == 200
    script = static.text
    assert 'fetch("/api/v1/analyze"' in script
    assert "Analyzing locally" in script
    assert "Analysis complete." in script
    assert "if (!response.ok)" in script
    assert "data.message" in script
