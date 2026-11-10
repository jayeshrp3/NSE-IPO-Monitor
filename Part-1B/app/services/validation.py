import re
from datetime import date

from app.schemas.extraction import (
    DATE_FIELDS,
    canonicalize_date_text,
    has_ambiguous_numeric_date,
)

RELATIONSHIPS = (
    ("opening_date", "closing_date", "chronology_opening_closing"),
    ("closing_date", "allotment_date", "chronology_closing_allotment"),
    ("allotment_date", "refund_date", "chronology_allotment_refund"),
    ("allotment_date", "listing_date", "chronology_allotment_listing"),
)

FIELD_TERMS = {
    "opening_date": re.compile(
        r"\b(?:opening(?:\s+date)?|opens?|open|subscription\s+begins|"
        r"bidding\s+begins)\b",
        re.IGNORECASE,
    ),
    "closing_date": re.compile(
        r"\b(?:closing(?:\s+date)?|closes?|close|subscription\s+ends|"
        r"bidding\s+ends)\b",
        re.IGNORECASE,
    ),
    "allotment_date": re.compile(r"\ballotment\b", re.IGNORECASE),
    "refund_date": re.compile(r"\brefunds?\b", re.IGNORECASE),
    "listing_date": re.compile(r"\b(?:listing|listed|lists?|trading\s+commences)\b", re.IGNORECASE),
}

MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

MONTH_PATTERN = "|".join(re.escape(name) for name in sorted(MONTHS, key=len, reverse=True))


def _check(check_id: str, passed: bool, message: str | None = None) -> dict:
    return {"check_id": check_id, "passed": passed, "message": message}


def _sentence_segment(source: str, start: int, stop: int) -> tuple[str, int]:
    """Return a field-local source segment, stopping at sentence punctuation."""
    raw = source[start:stop]
    boundary = re.search(r"[.;\n]", raw)
    if boundary:
        raw = raw[: boundary.start()]
    trimmed = raw.rstrip()
    return trimmed, start + len(trimmed)


def _unique_source_year(source: str) -> str:
    years = set(re.findall(r"\b20\d{2}\b", source))
    return next(iter(years)) if len(years) == 1 else ""


def _occurrences(source: str) -> list[tuple[int, int, str]]:
    found = []
    for field_name, pattern in FIELD_TERMS.items():
        found.extend((match.start(), match.end(), field_name) for match in pattern.finditer(source))
    return sorted(found, key=lambda item: (item[0], item[1]))


def _contains_impossible_month_date(text: str, year_text: str) -> bool:
    pattern = re.compile(
        rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_PATTERN})"
        rf"(?:,?\s+(20\d{{2}}))?\b",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        month = MONTHS.get(match.group(2).lower())
        actual_year = match.group(3) or year_text
        if month and actual_year:
            try:
                date(int(actual_year), month, int(match.group(1)))
            except ValueError:
                return True
    return False


def _date_evidence_for_value(
    source: str,
    field_name: str,
    value: str,
    occurrences: list[tuple[int, int, str]],
    year_text: str,
) -> str | None:
    """Return an exact source substring containing this field and date."""
    for index, (start, end, name) in enumerate(occurrences):
        if name != field_name:
            continue
        next_start = occurrences[index + 1][0] if index + 1 < len(occurrences) else len(source)
        segment, segment_end = _sentence_segment(source, end, next_start)
        if value in canonicalize_date_text(f"{segment} {year_text}"):
            return source[start:segment_end].strip()
    return None


def source_date_candidates(
    source: str,
) -> tuple[dict[str, set[str]], set[str], set[str]]:
    """Extract source-supported dates by nearby IPO field labels."""
    occurrences = _occurrences(source)
    year_text = _unique_source_year(source)
    candidates = {name: set() for name in DATE_FIELDS}
    ambiguous: set[str] = set()
    invalid: set[str] = set()

    for index, (_, end, field_name) in enumerate(occurrences):
        next_start = occurrences[index + 1][0] if index + 1 < len(occurrences) else len(source)
        segment, _ = _sentence_segment(source, end, next_start)
        candidates[field_name].update(canonicalize_date_text(f"{segment} {year_text}"))
        if has_ambiguous_numeric_date(segment):
            ambiguous.add(field_name)
        if _contains_impossible_month_date(segment, year_text):
            invalid.add(field_name)

    return candidates, ambiguous, invalid


def _dedupe_checks(checks: list[dict]) -> list[dict]:
    unique = {}
    for check in checks:
        key = (check["check_id"], check.get("message"))
        unique[key] = check
    return list(unique.values())


def validate_dates(fields: dict, source: str) -> dict:
    normalized = {
        name: dict(
            fields.get(name)
            or {
                "value": None,
                "status": "missing",
                "evidence": None,
                "message": "Not stated in the announcement.",
            }
        )
        for name in DATE_FIELDS
    }

    checks: list[dict] = []
    errors: list[str] = []
    candidates, ambiguous_fields, invalid_fields = source_date_candidates(source)
    occurrences = _occurrences(source)
    source_year = _unique_source_year(source)

    for name in DATE_FIELDS:
        item = normalized[name]
        value = item.get("value")

        if name in invalid_fields:
            item.update(
                value=None,
                status="invalid",
                message="The source states an impossible calendar date.",
            )
            error = f"{name} contains an impossible calendar date."
            errors.append(error)
            checks.append(_check("calendar_validity", False, error))
            continue

        if name in ambiguous_fields:
            item.update(
                value=None,
                status="ambiguous",
                message="The numeric date has multiple locale interpretations.",
            )
            error = f"{name} contains an ambiguous numeric date."
            errors.append(error)
            checks.append(_check("source_support", False, error))
            continue

        if len(candidates[name]) > 1:
            item.update(
                value=None,
                status="contradictory",
                message="The source contains conflicting dates for this field.",
            )
            error = f"{name} contains conflicting source dates."
            errors.append(error)
            checks.append(_check("source_support", False, error))
            continue

        if value is None and len(candidates[name]) == 1:
            value = next(iter(candidates[name]))
            item["value"] = value

        if value is None:
            if item.get("status") not in {"ambiguous", "contradictory", "invalid"}:
                item.update(status="missing", message="Date is not stated.")
            continue

        try:
            parsed_value = date.fromisoformat(value)
        except (ValueError, TypeError):
            item.update(
                value=None,
                status="invalid",
                message="Not a valid ISO calendar date.",
            )
            error = f"{name} is not a valid calendar date."
            errors.append(error)
            checks.append(_check("calendar_validity", False, error))
            continue

        if len(candidates[name]) != 1 or value not in candidates[name]:
            item.update(
                value=None,
                status="uncertain",
                message=(
                    "Date could not be independently matched to this IPO field in the source."
                ),
            )
            error = f"{name} is not independently supported by source evidence."
            errors.append(error)
            checks.append(_check("source_support", False, error))
            continue

        exact_evidence = _date_evidence_for_value(source, name, value, occurrences, source_year)
        if not exact_evidence:
            item.update(
                value=None,
                status="uncertain",
                message="Date evidence could not be located exactly in the source.",
            )
            error = f"{name} has no exact source evidence."
            errors.append(error)
            checks.append(_check("source_support", False, error))
            continue

        item.update(
            value=parsed_value.isoformat(),
            status="extracted",
            evidence=exact_evidence,
            message=None,
        )
        checks.extend(
            [
                _check("date_format", True, name),
                _check("calendar_validity", True, name),
                _check("source_support", True, name),
            ]
        )

    chronology_errors: list[tuple[str, str, str]] = []
    for earlier, later, check_id in RELATIONSHIPS:
        left = candidates[earlier]
        right = candidates[later]
        if len(left) != 1 or len(right) != 1:
            continue

        earlier_date = date.fromisoformat(next(iter(left)))
        later_date = date.fromisoformat(next(iter(right)))

        if earlier_date > later_date:
            chronology_errors.append((earlier, later, check_id))
            error = f"Chronology violation: {earlier} must not follow {later}."
            errors.append(error)
            checks.append(_check(check_id, False, error))
        elif normalized[earlier]["value"] is not None and normalized[later]["value"] is not None:
            checks.append(_check(check_id, True))

    if chronology_errors:
        # A broken IPO timeline makes the complete date sequence unreliable.
        # Invalidate every extracted date so callers cannot use a partial,
        # apparently valid timeline from an announcement with contradictions.
        for name in DATE_FIELDS:
            if normalized[name]["value"] is not None:
                normalized[name].update(
                    value=None,
                    status="contradictory",
                    message="The source dates violate the required IPO chronology.",
                )

    return {
        "fields": normalized,
        "validation": {
            "valid": not errors,
            "errors": errors,
            "checks": _dedupe_checks(checks),
        },
        "source_dates": {name: sorted(values) for name, values in candidates.items()},
    }
