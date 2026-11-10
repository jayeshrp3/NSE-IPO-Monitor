from pathlib import Path


def test_browser_renderer_uses_text_only_dom_operations():
    source = Path("app/static/app.js").read_text(encoding="utf-8")

    assert "textContent" in source
    assert "innerHTML" not in source
    assert "createElement" in source
