"""IPO application workflows."""

from datetime import date
from typing import Any

from app.core.config import Settings
from app.core.errors import IPODataError, ValidationError
from app.db.models import IPORecord
from app.db.repository import IPORepository
from app.services.alert_service import derive_alert_status
from app.services.status_service import derive_deadline_values, derive_status
from app.utils.dates import parse_iso_date, validate_ipo_dates
from app.utils.validation import OPTIONAL_DATE_FIELDS, validate_company_name


class IPOService:
    def __init__(self, repository: IPORepository, settings: Settings):
        self.repository = repository
        self.settings = settings

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        values = self._validated_values(payload)
        return self._serialize(self.repository.create(values))

    def get(self, ipo_id: int) -> dict[str, Any] | None:
        record = self.repository.get(ipo_id)
        return self._serialize(record) if record is not None else None

    def list(
        self,
        *,
        company_name: str | None = None,
        status: str | None = None,
        sort: str = "opening_date",
        order: str = "asc",
    ) -> list[dict[str, Any]]:
        if sort not in {"opening_date", "closing_date"}:
            raise ValidationError("sort must be opening_date or closing_date.")
        if order not in {"asc", "desc"}:
            raise ValidationError("order must be asc or desc.")
        if status is not None and status not in {"Upcoming", "Open", "Closed", "Listed"}:
            raise ValidationError("status must be Upcoming, Open, Closed, or Listed.")

        current_date = date.today()
        results = []
        query = company_name.strip().casefold() if company_name is not None else None
        for record in self.repository.list_all():
            serialized = self._serialize(record, current_date)
            if query and query not in record.company_name.casefold():
                continue
            if status is not None and serialized["status"] != status:
                continue
            results.append(serialized)

        results.sort(
            key=lambda item: (item[sort], item["id"]),
            reverse=False,
        )
        if order == "desc":
            # Keep the specified IPO-ID ascending tie-breaker in either order.
            results.sort(key=lambda item: item["id"])
            results.sort(key=lambda item: item[sort], reverse=True)
        return results

    def update(
        self,
        ipo_id: int,
        payload: dict[str, Any],
        fields_set: set[str],
    ) -> dict[str, Any] | None:
        existing = self.repository.get(ipo_id)
        if existing is None:
            return None

        merged: dict[str, Any] = {
            "company_name": existing.company_name,
            "opening_date": existing.opening_date,
            "closing_date": existing.closing_date,
            "allotment_date": existing.allotment_date,
            "refund_date": existing.refund_date,
            "listing_date": existing.listing_date,
        }
        for field in fields_set:
            if field in OPTIONAL_DATE_FIELDS and payload.get(field) is None:
                merged[field] = None
            elif payload.get(field) is not None:
                merged[field] = payload[field]
            else:
                raise ValidationError(f"{field} cannot be empty.")

        values = self._validated_values(merged)
        updated = self.repository.update(ipo_id, values)
        return self._serialize(updated) if updated is not None else None

    def delete(self, ipo_id: int) -> bool:
        return self.repository.delete(ipo_id)

    def _validated_values(self, payload: dict[str, Any]) -> dict[str, Any]:
        company_name = validate_company_name(payload.get("company_name"))
        opening_date = parse_iso_date(payload.get("opening_date"), "opening_date")
        closing_date = parse_iso_date(payload.get("closing_date"), "closing_date")
        optional_dates = {
            field: self._parse_optional(payload.get(field), field) for field in OPTIONAL_DATE_FIELDS
        }
        validate_ipo_dates(opening_date, closing_date, optional_dates["listing_date"])
        return {
            "company_name": company_name,
            "opening_date": opening_date,
            "closing_date": closing_date,
            **optional_dates,
        }

    @staticmethod
    def _parse_optional(value: Any, field: str) -> date | None:
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            raise ValidationError(f"{field} must be a YYYY-MM-DD string or empty.")
        return parse_iso_date(value, field)

    def _serialize(
        self,
        record: IPORecord | None,
        current_date: date | None = None,
    ) -> dict[str, Any]:
        if record is None:
            raise IPODataError("IPO record is unavailable.")
        for field in OPTIONAL_DATE_FIELDS:
            value = getattr(record, field)
            if value is not None:
                try:
                    parse_iso_date(value, field)
                except ValidationError as exc:
                    raise IPODataError(
                        f"Stored IPO data has an invalid {field}; the record cannot be displayed."
                    ) from exc
        current_date = current_date or date.today()
        return {
            "id": record.id,
            "company_name": record.company_name,
            "opening_date": record.opening_date,
            "closing_date": record.closing_date,
            "allotment_date": record.allotment_date,
            "refund_date": record.refund_date,
            "listing_date": record.listing_date,
            "status": derive_status(record, current_date),
            **derive_deadline_values(record, current_date),
            "alert_status": derive_alert_status(
                record, current_date, self.settings.alert_threshold
            ),
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }
