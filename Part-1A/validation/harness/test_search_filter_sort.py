"""Black-box search, status filtering, and stable ordering checks."""

from datetime import date, timedelta


def add(client, name, opening, closing):
    response = client.post(
        "/api/ipos",
        json={
            "company_name": name,
            "opening_date": opening.isoformat(),
            "closing_date": closing.isoformat(),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_search_is_trimmed_case_insensitive_substring_and_status_filters(client):
    today = date.today()
    add(client, "Searchable Pearl", today + timedelta(days=2), today + timedelta(days=4))
    add(client, "Unrelated Company", today + timedelta(days=3), today + timedelta(days=5))
    add(client, "Open status record", today - timedelta(days=1), today + timedelta(days=1))
    add(client, "Closed status record", today - timedelta(days=3), today - timedelta(days=1))
    closing = today - timedelta(days=10)
    listing = closing
    counted = 0
    while counted < 3:
        listing += timedelta(days=1)
        if listing.weekday() < 5:
            counted += 1
    add(client, "Listed status record", closing - timedelta(days=2), closing)
    listed_update = client.get(
        "/api/ipos", params={"company_name": "Listed status record"}
    ).json()
    assert len(listed_update) == 1
    client.put(
        f"/api/ipos/{listed_update[0]['id']}",
        json={"listing_date": listing.isoformat()},
    )

    matches = client.get("/api/ipos", params={"company_name": "  PEARL  "}).json()
    assert [item["company_name"] for item in matches] == ["Searchable Pearl"]

    for status in ("Upcoming", "Open", "Closed", "Listed"):
        filtered = client.get("/api/ipos", params={"status": status}).json()
        assert any(item["status"] == status for item in filtered)
        assert all(item["status"] == status for item in filtered)
    assert client.get("/api/ipos", params={"company_name": "no such company"}).json() == []
    assert (
        client.get("/api/ipos", params={"company_name": "' OR 1=1 --"}).json()
        == []
    )
    assert (
        client.get(
            "/api/ipos",
            params={"company_name": "no such company", "status": "Listed"},
        ).json()
        == []
    )

    before_search = client.get("/api/ipos").json()
    client.get(
        "/api/ipos",
        params={"company_name": "Pearl", "status": "Upcoming", "sort": "closing_date"},
    )
    after_search = client.get("/api/ipos").json()
    assert before_search == after_search


def test_sorting_supports_dates_and_ascending_id_tie_breaks(client):
    today = date.today()
    first = add(client, "Sort first", today + timedelta(days=10), today + timedelta(days=12))
    second = add(client, "Sort second", today + timedelta(days=10), today + timedelta(days=11))
    third = add(client, "Sort third", today + timedelta(days=9), today + timedelta(days=13))
    tied_update = client.put(
        f"/api/ipos/{first['id']}",
        json={
            "company_name": first["company_name"],
            "opening_date": first["opening_date"],
            "closing_date": second["closing_date"],
        },
    )
    assert tied_update.status_code == 200

    ascending = client.get(
        "/api/ipos", params={"sort": "opening_date", "order": "asc"}
    ).json()
    assert [item["id"] for item in ascending[:3]] == [third["id"], first["id"], second["id"]]

    descending = client.get(
        "/api/ipos", params={"sort": "opening_date", "order": "desc"}
    ).json()
    equal_date_ids = [
        item["id"] for item in descending if item["opening_date"] == first["opening_date"]
    ]
    assert equal_date_ids == sorted([first["id"], second["id"]])

    by_closing = client.get(
        "/api/ipos", params={"sort": "closing_date", "order": "asc"}
    ).json()
    assert [item["id"] for item in by_closing[:3]] == [
        first["id"],
        second["id"],
        third["id"],
    ]
    by_closing_descending = client.get(
        "/api/ipos", params={"sort": "closing_date", "order": "desc"}
    ).json()
    assert [item["id"] for item in by_closing_descending[:3]] == [
        third["id"],
        first["id"],
        second["id"],
    ]


def test_invalid_filter_and_sort_values_return_validation_errors(client):
    assert client.get("/api/ipos", params={"status": "Unknown"}).status_code == 422
    assert client.get("/api/ipos", params={"sort": "company_name"}).status_code == 422
