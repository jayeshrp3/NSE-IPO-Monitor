"""Validation helpers for incoming IPO data."""

from datetime import date
from typing import Any

from app.core.errors import ValidationError
from app.utils.dates import parse_iso_date, validate_ipo_dates

OPTIONAL_DATE_FIELDS = ("allotment_date", "refund_date", "listing_date")
DATE_FIELDS = ("opening_date", "closing_date", *OPTIONAL_DATE_FIELDS)


def normalize_optional_date(value: Any, field_name: str) -> date | None:
    """Map omitted/explicit-empty optional date values to None."""
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a YYYY-MM-DD string or empty.")
    return parse_iso_date(value, field_name)


def validate_company_name(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("company_name must not be empty.")
    return value.strip()


def validate_create_payload(payload: dict[str, Any]) -> dict[str, Any]:
    company_name = validate_company_name(payload.get("company_name"))
    opening_raw = payload.get("opening_date")
    closing_raw = payload.get("closing_date")
    if not isinstance(opening_raw, str) or not isinstance(closing_raw, str):
        raise ValidationError("opening_date and closing_date are required YYYY-MM-DD dates.")
    opening_date = parse_iso_date(opening_raw, "opening_date")
    closing_date = parse_iso_date(closing_raw, "closing_date")
    optional_dates = {
        field: normalize_optional_date(payload.get(field), field) for field in OPTIONAL_DATE_FIELDS
    }
    validate_ipo_dates(
        opening_date,
        closing_date,
        optional_dates["listing_date"],
    )
    return {
        "company_name": company_name,
        "opening_date": opening_date,
        "closing_date": closing_date,
        **optional_dates,
    }
