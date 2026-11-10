"""Company-name normalization used by duplicate detection."""

import re
from datetime import date


def normalize_company_name(company_name: str) -> str:
    """Trim, collapse whitespace, and case-fold a company name."""
    return re.sub(r"\s+", " ", company_name.strip()).casefold()


def matches_duplicate_identity(
    existing_company_name: str,
    existing_opening_date: str,
    existing_closing_date: str,
    candidate_company_name: str,
    candidate_opening_date: date,
    candidate_closing_date: date,
) -> bool:
    return (
        normalize_company_name(existing_company_name)
        == normalize_company_name(candidate_company_name)
        and existing_opening_date == candidate_opening_date.isoformat()
        and existing_closing_date == candidate_closing_date.isoformat()
    )
