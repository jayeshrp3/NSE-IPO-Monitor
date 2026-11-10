"""Exercise safe behavior when persisted IPO content is corrupted."""

import os
import sqlite3
import stat
from datetime import date, timedelta


def test_corrupt_persisted_date_surfaces_safe_error_without_rewrite(
    client, base_url, database_path
):
    assert base_url.startswith("http://127.0.0.1:")

    response = client.post(
        "/api/ipos",
        json={
            "company_name": "Corruption target",
            "opening_date": (date.today() + timedelta(days=1)).isoformat(),
            "closing_date": (date.today() + timedelta(days=3)).isoformat(),
        },
    )
    assert response.status_code == 201
    record_id = response.json()["id"]

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA ignore_check_constraints = ON")
        connection.execute(
            "UPDATE ipos SET closing_date = ? WHERE id = ?",
            ("not-a-date", record_id),
        )

    corrupted = client.get(f"/api/ipos/{record_id}")
    assert corrupted.status_code == 500
    assert "invalid closing_date" in corrupted.json()["detail"]
    with sqlite3.connect(database_path) as connection:
        saved_value = connection.execute(
            "SELECT closing_date FROM ipos WHERE id = ?", (record_id,)
        ).fetchone()[0]
    assert saved_value == "not-a-date"

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA ignore_check_constraints = ON")
        connection.execute(
            "UPDATE ipos SET closing_date = ?, allotment_date = ? WHERE id = ?",
            (
                (date.today() + timedelta(days=3)).isoformat(),
                "also-not-a-date",
                record_id,
            ),
        )
    corrupted_optional = client.get(f"/api/ipos/{record_id}")
    assert corrupted_optional.status_code == 500
    assert "invalid allotment_date" in corrupted_optional.json()["detail"]


def test_database_integrity_check_passes_after_valid_write(client, database_path):
    response = client.post(
        "/api/ipos",
        json={
            "company_name": "Integrity check",
            "opening_date": (date.today() + timedelta(days=1)).isoformat(),
            "closing_date": (date.today() + timedelta(days=3)).isoformat(),
        },
    )
    assert response.status_code == 201
    with sqlite3.connect(database_path) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    assert integrity == "ok"


def test_corrupted_database_returns_safe_read_error_without_rewrite(client, database_path):
    database_path.write_bytes(b"not a SQLite database")
    response = client.get("/api/ipos")
    assert response.status_code == 503
    assert "database error" in response.json()["detail"]
    assert database_path.read_bytes() == b"not a SQLite database"


def test_read_only_database_returns_safe_write_error(client, database_path):
    original_mode = database_path.stat().st_mode
    os.chmod(database_path, stat.S_IREAD)
    try:
        response = client.post(
            "/api/ipos",
            json={
                "company_name": "Read-only database",
                "opening_date": (date.today() + timedelta(days=1)).isoformat(),
                "closing_date": (date.today() + timedelta(days=3)).isoformat(),
            },
        )
        assert response.status_code == 503
        assert "database error" in response.json()["detail"]
    finally:
        os.chmod(database_path, original_mode | stat.S_IWRITE)
