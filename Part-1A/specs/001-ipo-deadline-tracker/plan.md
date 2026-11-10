# Implementation Plan: IPO Deadline Tracker

**Branch**: `[001-ipo-deadline-tracker]` | **Date**: 2026-11-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-ipo-deadline-tracker/spec.md`

## Summary

Implement a deterministic, manually maintained IPO watchlist as a single FastAPI
web application with a server-rendered Bootstrap interface and SQLite storage.
Routes, domain services, validation, persistence, and presentation remain
separate. Status, signed days remaining, elapsed days, and alert state are
derived from validated records and the current date; they are not stored as
canonical IPO fields.

The application rejects duplicate records using normalized company name plus
opening and closing dates. A provided listing date must be at least three
Monday-to-Friday working days after closing; weekends are skipped and public
holidays are not. No live NSE integration, trading, payments, or AI extraction
is included.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, Bootstrap, Pytest, HTTPX
and Playwright for the independent black-box harness, Ruff, Bandit; Python
`sqlite3` from the standard library

**Storage**: SQLite database storing IPO input fields and created/updated
timestamps; computed status and deadline values are derived at read time

**Testing**: Independent Pytest contract/integration harness against the
application's HTTP interface; Ruff and Bandit quality gates

**Target Platform**: Local or server-hosted Python web application

**Project Type**: Single web application with JSON API and server-rendered UI

**Performance Goals**: Personal/small-user watchlist; no high-load service-level
target is specified

**Constraints**: Deterministic business rules; parameterized SQL; no hardcoded
secrets; explicit safe errors; public holidays are not excluded from the
three-working-day listing rule; required test evidence and human decision

**Scale/Scope**: Manual or sample historical IPO records; no live NSE API,
trading, payment, or AI features

## Constitution Check

*GATE: Must pass before implementation. Re-check after design and validation.*

- Pass: Python, FastAPI, and SQLite satisfy the constitution.
- Pass: API/web routes, services, validation, persistence, and templates are
  separated.
- Pass: IPO calculations and persistence rules are explicit, deterministic,
  parameterized, and testable.
- Pass: The mandatory validation harness is separate from application modules
  and exercises the public HTTP contract without importing implementation code.
- Pass: Pytest, Ruff, Bandit, actual run evidence, repair/rerun evidence, and a
  human ACCEPT/REJECT decision are required gates.
- Pass: No secrets or out-of-scope external data/trading capabilities are
  introduced.

## Technical Decisions

- **Persistence**: Use Python's standard-library `sqlite3` module, not an ORM.
  Keep SQL in the repository layer and bind all user values as query
  parameters. This avoids an unnecessary dependency for the single-table scope.
- **Threshold configuration**: Read `IPO_ALERT_THRESHOLD` at application
  startup; default to `3`. Reject a non-integer or negative value explicitly.
  The value is an application setting, not a per-record or persisted value.
- **Database configuration**: Read the database location from
  `IPO_DATABASE_PATH`; the harness supplies an isolated path for each run.
- **Date calculations**: Use calendar dates, not timestamps, for IPO boundaries.
  Count the three weekdays strictly after closing; Monday-Friday count and
  Saturday/Sunday do not. Public holidays count as weekdays because no holiday
  calendar is in scope.
- **Search and sorting**: Apply trimmed, Unicode case-insensitive substring
  search, derived-status filtering, and allow-listed date sorting in the service
  layer over repository results. This preserves Python `casefold()` behavior;
  search text is never interpolated into SQL. Repository SQL remains
  parameterized for all supplied values.
- **Expired representation**: Return signed `days_remaining =
  closing_date - current_date`. When negative, also return positive
  `expired_days`; the UI displays an expired label and elapsed days, never a
  positive countdown.
- **Duplicate normalization**: Trim edge whitespace, collapse repeated
  internal whitespace, then compare names case-insensitively with case folding.
  Keep the user's display name otherwise unchanged. Reject a duplicate with a
  clear conflict response.
- **Independent validation**: Acceptance, contract, and integration tests live
  under `validation/harness/`, use a configured base URL and isolated test
  database, and do not import `app` modules. Developer-only checks must not
  replace or weaken this harness.
- **Evidence workflow**: Keep `harness-log.md` at the Part 1A root. Preserve
  initial and repaired source/evidence snapshots under
  `validation/evidence/initial/` and `validation/evidence/repaired/`; record
  exact commands, outputs, failures, repairs, and reruns. Rerun the same gates
  after each repair and obtain a human ACCEPT or REJECT decision.

## Project Structure

### Documentation (this feature)

```text
specs/001-ipo-deadline-tracker/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ipo-api.md
├── checklists/
│   └── requirements.md
├── spec.md
└── tasks.md
```

### Application and independent validation harness

```text
app/
├── api/
│   ├── deps.py
│   └── routes/
│       └── ipos.py
├── core/
│   ├── config.py
│   └── errors.py
├── db/
│   ├── connection.py
│   ├── models.py
│   └── repository.py
├── schemas/
│   └── ipo.py
├── services/
│   ├── alert_service.py
│   ├── duplicate_service.py
│   ├── ipo_service.py
│   └── status_service.py
├── utils/
│   ├── dates.py
│   ├── normalization.py
│   └── validation.py
├── web/
│   └── routes.py
└── main.py                 # Mount API/web routes, templates, and static assets

frontend/
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
└── templates/
    ├── base.html
    ├── ipo_detail.html
    ├── ipo_form.html
    └── ipo_list.html

validation/
├── harness/
│   ├── conftest.py         # Launch/configure app externally; no app imports
│   ├── test_api_contract.py
│   ├── test_crud_and_validation.py
│   ├── test_dates_and_alerts.py
│   ├── test_search_filter_sort.py
│   ├── test_corrupted_data.py
│   └── test_ui_flows.py
└── evidence/
    ├── initial/
    └── repaired/

harness-log.md              # Actual commands, results, repairs, reruns, decision
```

**Structure Decision**: Use one deployable application and a separately
maintained black-box validation harness. FastAPI's application bootstrap mounts
the API router, server-rendered web router, template directory, and static
assets. Frontend routes remain presentation/request handling only; IPO rules
stay in services.

## Requirement Traceability

The task list assigns implementation and independent validation tasks to every
FR and buildable SC. The task-list traceability matrix is the acceptance index;
human-only review criterion SC-006 is additionally recorded in
`harness-log.md`.

## Complexity Tracking

No constitution violations or additional architectural projects are proposed.
