"""Deterministic IPO state and deadline derivation."""

from datetime import date
from typing import Any

from app.core.errors import IPODataError, ValidationError
from app.db.models import IPORecord
from app.utils.dates import add_working_days, parse_iso_date


def derive_status(record: IPORecord, current_date: date) -> str:
    opening_date = _stored_date(record.opening_date, "opening_date")
    closing_date = _stored_date(record.closing_date, "closing_date")
    listing_date = (
        _stored_date(record.listing_date, "listing_date")
        if record.listing_date is not None
        else None
    )
    if closing_date < opening_date:
        raise IPODataError("Stored IPO data has an invalid opening/closing date sequence.")
    if listing_date is not None and listing_date < add_working_days(closing_date, 3):
        raise IPODataError("Stored IPO data has an invalid listing_date.")

    if current_date < opening_date:
        return "Upcoming"
    if current_date <= closing_date:
        return "Open"
    if listing_date is not None and current_date >= listing_date:
        return "Listed"
    return "Closed"


def derive_deadline_values(record: IPORecord, current_date: date) -> dict[str, Any]:
    closing_date = _stored_date(record.closing_date, "closing_date")
    days_remaining = (closing_date - current_date).days
    expired_days = -days_remaining if days_remaining < 0 else None
    return {
        "days_remaining": days_remaining,
        "expired_days": expired_days,
        "deadline_expired": expired_days is not None,
    }


def _stored_date(value: str, field_name: str) -> date:
    try:
        return parse_iso_date(value, field_name)
    except ValidationError as exc:
        raise IPODataError(
            f"Stored IPO data has an invalid {field_name}; status cannot be calculated."
        ) from exc
