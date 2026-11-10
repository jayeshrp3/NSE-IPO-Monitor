"""Strict date parsing and IPO working-day calculations."""

from datetime import date, timedelta

from app.core.errors import ValidationError


def parse_iso_date(value: str, field_name: str) -> date:
    """Parse only canonical YYYY-MM-DD values and report field-specific errors."""
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid date in YYYY-MM-DD format.") from exc
    if parsed.isoformat() != value:
        raise ValidationError(f"{field_name} must be a valid date in YYYY-MM-DD format.")
    return parsed


def add_working_days(start_date: date, working_days: int) -> date:
    """Count weekdays strictly after start_date; public holidays count as weekdays."""
    if working_days < 0:
        raise ValueError("working_days must be non-negative")
    current = start_date
    counted = 0
    while counted < working_days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            counted += 1
    return current


def validate_ipo_dates(
    opening_date: date,
    closing_date: date,
    listing_date: date | None,
) -> None:
    """Validate date ordering required by the IPO domain rules."""
    if closing_date < opening_date:
        raise ValidationError("closing_date cannot be earlier than opening_date.")

    minimum_listing_date = add_working_days(closing_date, 3)
    if listing_date is not None and listing_date < minimum_listing_date:
        raise ValidationError(
            "listing_date must be on or after three weekdays strictly after closing_date "
            "(weekends excluded; public holidays are not excluded)."
        )
