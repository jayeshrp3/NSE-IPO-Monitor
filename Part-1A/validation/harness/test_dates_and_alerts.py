"""Independent date-boundary, listing weekday, and threshold checks."""

from datetime import date, timedelta

import pytest


def payload(company_name, opening, closing, listing=None):
    return {
        "company_name": company_name,
        "opening_date": opening.isoformat(),
        "closing_date": closing.isoformat(),
        "listing_date": listing.isoformat() if listing else None,
    }


def create_record(client, company_name, opening, closing, listing=None):
    response = client.post(
        "/api/ipos",
        json=payload(company_name, opening, closing, listing),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_status_opening_closing_listing_and_expiry_boundaries(client):
    today = date.today()
    upcoming = create_record(
        client,
        "Upcoming boundary",
        today + timedelta(days=1),
        today + timedelta(days=4),
    )
    opening_boundary = create_record(client, "Opening boundary", today, today)
    expired = create_record(
        client,
        "Expired boundary",
        today - timedelta(days=5),
        today - timedelta(days=1),
    )

    closing = today - timedelta(days=10)
    minimum_listing = closing
    counted = 0
    while counted < 3:
        minimum_listing += timedelta(days=1)
        if minimum_listing.weekday() < 5:
            counted += 1
    listed = create_record(
        client,
        "Listing boundary",
        closing - timedelta(days=3),
        closing,
        minimum_listing,
    )
    listing_today = today
    closing_before_listing = listing_today
    weekdays_before = 0
    while weekdays_before < 3:
        closing_before_listing -= timedelta(days=1)
        if closing_before_listing.weekday() < 5:
            weekdays_before += 1
    closed_before_listing = create_record(
        client,
        "Before listing boundary",
        closing_before_listing - timedelta(days=1),
        closing_before_listing,
        listing_today + timedelta(days=1),
    )
    listed_on_boundary = create_record(
        client,
        "On listing boundary",
        closing_before_listing - timedelta(days=1),
        closing_before_listing,
        listing_today,
    )

    assert upcoming["status"] == "Upcoming"
    assert upcoming["days_remaining"] == 4
    assert opening_boundary["status"] == "Open"
    assert opening_boundary["days_remaining"] == 0
    assert opening_boundary["alert_status"] == "Approaching"
    assert expired["status"] == "Closed"
    assert expired["days_remaining"] == -1
    assert expired["expired_days"] == 1
    assert expired["alert_status"] == "Expired"
    assert listed["status"] == "Listed"
    assert closed_before_listing["status"] == "Closed"
    assert listed_on_boundary["status"] == "Listed"


def test_listing_date_requires_three_weekdays_not_calendar_days(client):
    closing = date(2026, 1, 9)  # Friday
    accepted = create_record(
        client,
        "Weekday listing accepted",
        closing - timedelta(days=2),
        closing,
        date(2026, 1, 14),  # Wednesday; Tuesday is the second weekday
    )
    assert accepted["listing_date"] == "2026-01-14"

    rejected = client.post(
        "/api/ipos",
        json=payload(
            "Weekday listing rejected",
            closing - timedelta(days=1),
            closing,
            date(2026, 1, 13),
        ),
    )
    assert rejected.status_code == 422
    assert "three weekdays" in rejected.json()["detail"]


def test_alert_threshold_is_inclusive_and_only_for_open_records(client):
    today = date.today()
    at_threshold = create_record(
        client,
        "At threshold",
        today - timedelta(days=1),
        today + timedelta(days=3),
    )
    beyond_threshold = create_record(
        client,
        "Beyond threshold",
        today - timedelta(days=1),
        today + timedelta(days=4),
    )
    assert at_threshold["status"] == "Open"
    assert at_threshold["days_remaining"] == 3
    assert at_threshold["alert_status"] == "Approaching"
    assert beyond_threshold["status"] == "Open"
    assert beyond_threshold["alert_status"] == "None"


@pytest.mark.parametrize("base_url", [None], indirect=True)
def test_default_alert_threshold_is_three_calendar_days(client):
    today = date.today()
    response = client.post(
        "/api/ipos",
        json=payload(
            "Default threshold",
            today - timedelta(days=1),
            today + timedelta(days=3),
        ),
    )
    assert response.status_code == 201
    assert response.json()["alert_status"] == "Approaching"


@pytest.mark.parametrize("base_url", [0], indirect=True)
def test_zero_alert_threshold_includes_the_closing_date(client):
    today = date.today()
    response = client.post(
        "/api/ipos",
        json=payload("Zero threshold", today - timedelta(days=1), today),
    )
    assert response.status_code == 201
    assert response.json()["days_remaining"] == 0
    assert response.json()["alert_status"] == "Approaching"


@pytest.mark.parametrize("base_url", [5], indirect=True)
def test_configured_positive_alert_threshold(client):
    today = date.today()
    response = client.post(
        "/api/ipos",
        json=payload(
            "Configured threshold",
            today - timedelta(days=1),
            today + timedelta(days=5),
        ),
    )
    assert response.status_code == 201
    assert response.json()["days_remaining"] == 5
    assert response.json()["alert_status"] == "Approaching"
