"""Transport schemas for IPO creation and partial updates."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

OPTIONAL_DATE_FIELDS = ("allotment_date", "refund_date", "listing_date")

IPOStatus = Literal["Upcoming", "Open", "Closed", "Listed"]
IPOAlertStatus = Literal["None", "Approaching", "Expired"]


class IPOResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    company_name: str
    opening_date: str
    closing_date: str
    allotment_date: str | None
    refund_date: str | None
    listing_date: str | None
    status: IPOStatus
    days_remaining: int
    expired_days: int | None
    deadline_expired: bool
    alert_status: IPOAlertStatus
    created_at: str
    updated_at: str


class IPOCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_name: str
    opening_date: str
    closing_date: str
    allotment_date: str | None = None
    refund_date: str | None = None
    listing_date: str | None = None

    @field_validator(*OPTIONAL_DATE_FIELDS, mode="before")
    @classmethod
    def empty_optional_dates_are_none(cls, value: object) -> object:
        return None if value == "" else value


class IPOUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_name: str | None = None
    opening_date: str | None = None
    closing_date: str | None = None
    allotment_date: str | None = None
    refund_date: str | None = None
    listing_date: str | None = None

    @field_validator(*OPTIONAL_DATE_FIELDS, mode="before")
    @classmethod
    def empty_optional_dates_are_none(cls, value: object) -> object:
        return None if value == "" else value
