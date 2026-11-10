"""CRUD, validation, duplicate handling, and optional-date update semantics."""

from datetime import date, timedelta


def valid_payload(company_name="Northstar Foods", **overrides):
    opening = date.today() + timedelta(days=10)
    payload = {
        "company_name": company_name,
        "opening_date": opening.isoformat(),
        "closing_date": (opening + timedelta(days=4)).isoformat(),
        "allotment_date": None,
        "refund_date": None,
        "listing_date": None,
    }
    payload.update(overrides)
    return payload


def test_create_list_detail_and_delete(client):
    opening = date.today() + timedelta(days=10)
    closing = opening + timedelta(days=4)
    listing = closing
    working_days = 0
    while working_days < 3:
        listing += timedelta(days=1)
        if listing.weekday() < 5:
            working_days += 1
    response = client.post(
        "/api/ipos",
        json=valid_payload(
            opening_date=opening.isoformat(),
            closing_date=closing.isoformat(),
            allotment_date="2026-12-01",
            refund_date="2026-12-02",
            listing_date=listing.isoformat(),
        ),
    )
    assert response.status_code == 201
    record = response.json()
    assert record["company_name"] == "Northstar Foods"
    assert record["allotment_date"] == "2026-12-01"
    assert record["refund_date"] == "2026-12-02"
    assert record["listing_date"] == listing.isoformat()
    assert record["status"] in {"Upcoming", "Open", "Closed", "Listed"}
    assert isinstance(record["days_remaining"], int)
    assert record["created_at"]
    assert record["updated_at"]
    assert client.get(f"/api/ipos/{record['id']}").json() == record
    assert any(item["id"] == record["id"] for item in client.get("/api/ipos").json())

    assert client.delete(f"/api/ipos/{record['id']}").status_code == 204
    assert client.get(f"/api/ipos/{record['id']}").status_code == 404


def test_invalid_required_fields_dates_and_order_are_rejected(client):
    baseline = valid_payload("Invalid cases")
    cases = [
        (
            {**baseline, "company_name": "  "},
            "company_name must not be empty.",
        ),
        (
            {key: value for key, value in baseline.items() if key != "opening_date"},
            "Request validation failed.",
        ),
        (
            {key: value for key, value in baseline.items() if key != "closing_date"},
            "Request validation failed.",
        ),
        (
            {**baseline, "opening_date": "2026-02-30"},
            "opening_date must be a valid date in YYYY-MM-DD format.",
        ),
        (
            {**baseline, "allotment_date": "2026-02-30"},
            "allotment_date must be a valid date in YYYY-MM-DD format.",
        ),
        (
            {
                **baseline,
                "opening_date": "2026-05-10",
                "closing_date": "2026-05-09",
            },
            "closing_date cannot be earlier than opening_date.",
        ),
    ]
    for payload, expected_detail in cases:
        response = client.post("/api/ipos", json=payload)
        assert response.status_code == 422
        assert response.json()["detail"] == expected_detail


def test_update_preserves_omitted_optional_and_clears_explicit_empty(client):
    response = client.post(
        "/api/ipos",
        json=valid_payload(
            "Optional dates",
            allotment_date="2026-12-01",
            refund_date="2026-12-02",
        ),
    )
    assert response.status_code == 201
    record = response.json()
    updated = client.put(
        f"/api/ipos/{record['id']}",
        json={"company_name": "Optional dates updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["allotment_date"] == "2026-12-01"
    assert updated.json()["refund_date"] == "2026-12-02"

    cleared = client.put(
        f"/api/ipos/{record['id']}",
        json={"allotment_date": "", "refund_date": None},
    )
    assert cleared.status_code == 200
    assert cleared.json()["allotment_date"] is None
    assert cleared.json()["refund_date"] is None

    invalid = client.put(
        f"/api/ipos/{record['id']}",
        json={"listing_date": "not-a-date"},
    )
    assert invalid.status_code == 422
    persisted = client.get(f"/api/ipos/{record['id']}").json()
    assert persisted["company_name"] == "Optional dates updated"


def test_duplicate_identity_is_rejected_but_distinct_keys_are_allowed(client):
    payload = valid_payload(
        "  Acme   Industries ",
        opening_date="2027-01-10",
        closing_date="2027-01-15",
    )
    first = client.post("/api/ipos", json=payload)
    assert first.status_code == 201
    duplicate = client.post(
        "/api/ipos",
        json={
            **payload,
            "company_name": "acme industries",
        },
    )
    assert duplicate.status_code == 409
    assert "duplicate" in duplicate.json()["detail"].lower()

    distinct = client.post(
        "/api/ipos",
        json={**payload, "company_name": "Acme Industries", "closing_date": "2027-01-16"},
    )
    assert distinct.status_code == 201
    update_duplicate = client.put(
        f"/api/ipos/{first.json()['id']}",
        json={
            "company_name": "Acme Industries",
            "opening_date": "2027-01-10",
            "closing_date": "2027-01-16",
        },
    )
    assert update_duplicate.status_code == 409


def test_historical_records_remain_until_explicitly_deleted(client):
    response = client.post(
        "/api/ipos",
        json=valid_payload(
            "Historical retention",
            opening_date="2020-01-01",
            closing_date="2020-01-03",
        ),
    )
    assert response.status_code == 201
    record_id = response.json()["id"]
    assert client.get(f"/api/ipos/{record_id}").status_code == 200
    assert client.get(f"/api/ipos/{record_id}").json()["company_name"] == "Historical retention"
