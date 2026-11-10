# IPO API Contract

This contract describes the API surface for the Part 1A IPO Deadline Tracker. The design uses a JSON-over-HTTP API with FastAPI endpoints and a server-rendered HTML interface for direct user management.

## Endpoints

### POST /api/ipos

Create a new IPO record.

**Request body**:

```json
{
  "company_name": "ABC Ltd",
  "opening_date": "2026-12-10",
  "closing_date": "2026-12-15",
  "allotment_date": "2026-12-20",
  "refund_date": "2026-12-24",
  "listing_date": "2026-12-28"
}
```

**Validation**:
- `company_name` required and non-empty
- `opening_date` and `closing_date` required
- `closing_date` must be on or after `opening_date`
- `listing_date`, if provided, must be at least three Monday-to-Friday working days strictly after `closing_date`; Saturdays and Sundays are skipped and public holidays are not excluded
- malformed dates are rejected with clear validation errors
- duplicates are rejected when normalized company name, opening date, and closing date match; name comparison trims outer whitespace, collapses repeated internal whitespace, and case-folds

**Response**:
- HTTP 201 on success
- HTTP 422 on validation failure
- HTTP 409 on duplicate detection
- duplicate response includes a clear, user-safe explanation of the matching duplicate identity

### GET /api/ipos

Return all IPO records.

**Query parameters**:
- `status` optional (Upcoming, Open, Closed, Listed)
- `company_name` optional trimmed, case-insensitive substring search term
- `sort` optional (`opening_date`, `closing_date`)
- `order` optional (`asc`, `desc`); defaults to `asc`
- equal sort dates are ordered by IPO ID ascending

**Response**:
- JSON array of IPO records, each with fields and derived status metadata

### GET /api/ipos/{id}

Return a single IPO by record identifier.

**Response**:
- HTTP 200 with the record
- HTTP 404 when the record does not exist

### PUT /api/ipos/{id}

Update an IPO record.

**Semantics**:
- omitted optional fields preserve existing values
- explicit empty values clear the optional date
- required fields must remain valid after update
- update is rejected with HTTP 409 if the resulting record duplicates another record

**Response**:
- HTTP 200 on success
- HTTP 404 on missing record
- HTTP 422 on validation failure

### DELETE /api/ipos/{id}

Delete a record. The web UI MUST request explicit user confirmation before
sending this request; canceling confirmation MUST send no delete request.

**Response**:
- HTTP 200 or HTTP 204 on success
- HTTP 404 on missing record

Search, status filtering, and sorting are query parameters on `GET /api/ipos`;
there is no separate search endpoint.

## Application Configuration

- `IPO_ALERT_THRESHOLD` is a non-negative integer number of calendar days.
- If unset, it defaults to `3`.
- A malformed or negative value prevents application startup with an explicit
  configuration error; it is never silently coerced.
- This configuration is application-wide and is not stored per IPO.

## Shared Response Shape

```json
{
  "id": 1,
  "company_name": "ABC Ltd",
  "opening_date": "2026-12-10",
  "closing_date": "2026-12-15",
  "allotment_date": "2026-12-20",
  "refund_date": "2026-12-24",
  "listing_date": "2026-12-28",
  "status": "Upcoming",
  "days_remaining": 35,
  "expired_days": null,
  "alert_status": "None",
  "created_at": "2026-11-10T14:00:00Z",
  "updated_at": "2026-11-10T14:00:00Z"
}
```

`days_remaining` is the signed calendar-day difference `closing_date -
current_date`. For an expired IPO, it is negative and `expired_days` is the
positive elapsed-day count; the UI presents the expired indicator and elapsed
count rather than a positive countdown. `alert_status` is `Expired` after
closing, `Approaching` only when status is Open and `days_remaining` is between
zero and the configured threshold inclusive, and `None` otherwise.

## Notes

- Status, days remaining, and alert_status are computed from the business rules rather than treated as permanently stored values unless justified.
- Part 1A does not integrate a public-holiday calendar; public holidays on weekdays count as working days for listing-date validation.
- No API contract is defined for live NSE data or trading; those are explicitly out of scope for Part 1A.
