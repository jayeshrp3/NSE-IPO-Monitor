"""IPO duplicate identity policy."""

from datetime import date

from app.utils.normalization import matches_duplicate_identity


def is_duplicate(
    existing_company_name: str,
    existing_opening_date: str,
    existing_closing_date: str,
    company_name: str,
    opening_date: date,
    closing_date: date,
) -> bool:
    return matches_duplicate_identity(
        existing_company_name,
        existing_opening_date,
        existing_closing_date,
        company_name,
        opening_date,
        closing_date,
    )
