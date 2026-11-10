import re
from datetime import date
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

FieldStatus = Literal["extracted", "missing", "ambiguous", "contradictory", "invalid", "uncertain"]
ModelFieldStatus = Literal[
    "extracted",
    "missing",
    "ambiguous",
    "contradictory",
    "invalid",
    "uncertain",
    "inferred",
]
CheckId = Literal[
    "date_format",
    "calendar_validity",
    "source_support",
    "chronology_opening_closing",
    "chronology_closing_allotment",
    "chronology_allotment_refund",
    "chronology_allotment_listing",
]
NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
IsoDate = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2}$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class AnalysisRequest(StrictModel):
    announcement_text: Annotated[str, StringConstraints(min_length=1, max_length=50_000)]

    @field_validator("announcement_text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Announcement text must not be blank")
        return value


class FieldResult(StrictModel):
    value: str | None
    status: FieldStatus
    evidence: NonBlank | None
    message: NonBlank | None

    @model_validator(mode="after")
    def enforce_value_status(self):
        if (self.status == "extracted") != (self.value is not None):
            raise ValueError("Only extracted fields may contain a value")
        return self


class CompanyFieldResult(FieldResult):
    value: NonBlank | None


class DateFieldResult(FieldResult):
    value: IsoDate | None

    @field_validator("value")
    @classmethod
    def require_real_calendar_date(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Date must be a valid ISO calendar date") from exc
        return value


class ValidationCheck(StrictModel):
    check_id: CheckId
    passed: bool
    message: NonBlank | None


class ValidationResult(StrictModel):
    valid: bool
    errors: list[NonBlank]
    checks: list[ValidationCheck]


class AnalysisResponse(StrictModel):
    schema_version: Literal["1.0"]
    company_name: CompanyFieldResult
    opening_date: DateFieldResult
    closing_date: DateFieldResult
    allotment_date: DateFieldResult
    refund_date: DateFieldResult
    listing_date: DateFieldResult
    summary: NonBlank
    warnings: list[NonBlank]
    validation: ValidationResult
    injection_detected: bool


class ApiError(StrictModel):
    code: Literal[
        "invalid_request",
        "input_too_large",
        "invalid_model_output",
        "ollama_unavailable",
        "inference_timeout",
    ]
    message: NonBlank


class ModelFieldResult(StrictModel):
    value: str | None
    status: ModelFieldStatus
    evidence: NonBlank | None
    message: NonBlank | None


class ModelExtraction(StrictModel):
    company_name: ModelFieldResult | None = None
    opening_date: ModelFieldResult | None = None
    closing_date: ModelFieldResult | None = None
    allotment_date: ModelFieldResult | None = None
    refund_date: ModelFieldResult | None = None
    listing_date: ModelFieldResult | None = None
    summary: NonBlank
    warnings: list[NonBlank] = Field(default_factory=list)


DATE_FIELDS = (
    "opening_date",
    "closing_date",
    "allotment_date",
    "refund_date",
    "listing_date",
)


def canonicalize_date_text(text: str) -> set[str]:
    months = {
        name.lower(): number
        for number, names in enumerate(
            (
                (),
                ("January", "Jan"),
                ("February", "Feb"),
                ("March", "Mar"),
                ("April", "Apr"),
                ("May",),
                ("June", "Jun"),
                ("July", "Jul"),
                ("August", "Aug"),
                ("September", "Sep", "Sept"),
                ("October", "Oct"),
                ("November", "Nov"),
                ("December", "Dec"),
            )
        )
        for name in names
    }
    years = set(re.findall(r"\b(20\d{2})\b", text))
    year = int(next(iter(years))) if len(years) == 1 else None
    found: set[str] = set()
    month_pattern = "|".join(re.escape(name) for name in sorted(months, key=len, reverse=True))
    pattern = re.compile(
        rf"\b(\d{{1,2}}(?:st|nd|rd|th)?)\s+({month_pattern})(?:,?\s+(20\d{{2}}))?\b"
        rf"|\b({month_pattern})\s+(\d{{1,2}}(?:st|nd|rd|th)?)(?:,?\s+(20\d{{2}}))?\b",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        if match.group(1):
            day, month_name, explicit_year = match.group(1), match.group(2), match.group(3)
        else:
            month_name, day, explicit_year = match.group(4), match.group(5), match.group(6)
        month = months.get(month_name.lower())
        actual_year = int(explicit_year) if explicit_year else year
        if month and actual_year:
            try:
                day_number = int(re.match(r"\d{1,2}", day).group(0))
                found.add(date(actual_year, month, day_number).isoformat())
            except ValueError:
                continue
    for match in re.finditer(r"\b(20\d{2})-(\d{2})-(\d{2})\b", text):
        try:
            found.add(date(*(int(part) for part in match.groups())).isoformat())
        except ValueError:
            continue
    for match in re.finditer(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b", text):
        first, second, numeric_year = map(int, match.groups())
        if first <= 12 and second <= 12:
            continue
        month, day = (first, second) if first <= 12 else (second, first)
        try:
            found.add(date(numeric_year, month, day).isoformat())
        except ValueError:
            continue
    return found


def has_ambiguous_numeric_date(text: str) -> bool:
    return any(
        int(first) <= 12 and int(second) <= 12
        for first, second, _ in re.findall(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b", text)
    )
