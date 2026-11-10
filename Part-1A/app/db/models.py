"""IPO persistence record representation."""

from dataclasses import dataclass
from typing import Any

from app.core.errors import IPODataError


@dataclass(frozen=True)
class IPORecord:
    id: int
    company_name: str
    opening_date: str
    closing_date: str
    allotment_date: str | None
    refund_date: str | None
    listing_date: str | None
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "IPORecord":
        required_fields = (
            "id",
            "company_name",
            "opening_date",
            "closing_date",
            "allotment_date",
            "refund_date",
            "listing_date",
            "created_at",
            "updated_at",
        )
        if any(field not in row for field in required_fields):
            raise IPODataError("Stored IPO data is missing required fields.")

        if type(row["id"]) is not int:
            raise IPODataError("Stored IPO data has an invalid record identifier.")
        if not isinstance(row["company_name"], str) or not row["company_name"].strip():
            raise IPODataError("Stored IPO data has an invalid company name.")
        for field in ("opening_date", "closing_date", "created_at", "updated_at"):
            if not isinstance(row[field], str) or not row[field]:
                raise IPODataError(f"Stored IPO data has an invalid {field}.")
        for field in ("allotment_date", "refund_date", "listing_date"):
            if row[field] is not None and not isinstance(row[field], str):
                raise IPODataError(f"Stored IPO data has an invalid {field}.")

        return cls(
            id=row["id"],
            company_name=row["company_name"],
            opening_date=row["opening_date"],
            closing_date=row["closing_date"],
            allotment_date=row["allotment_date"],
            refund_date=row["refund_date"],
            listing_date=row["listing_date"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
