"""Deadline-alert derivation."""

from datetime import date

from app.db.models import IPORecord
from app.services.status_service import derive_deadline_values, derive_status


def derive_alert_status(record: IPORecord, current_date: date, threshold: int) -> str:
    deadline_values = derive_deadline_values(record, current_date)
    if deadline_values["deadline_expired"]:
        return "Expired"
    if (
        derive_status(record, current_date) == "Open"
        and 0 <= deadline_values["days_remaining"] <= threshold
    ):
        return "Approaching"
    return "None"
