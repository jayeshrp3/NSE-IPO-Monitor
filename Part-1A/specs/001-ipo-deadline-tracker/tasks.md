# Tasks: IPO Deadline Tracker

**Input**: Design documents from `/specs/001-ipo-deadline-tracker/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/,
quickstart.md, and the project constitution.

**Testing**: Mandatory acceptance checks are independent black-box Pytest
contract/integration tests in `validation/harness/`; they MUST NOT import
application implementation modules. Ruff and Bandit are required gates.

**Organization**: Tasks are grouped by user story after shared setup and
foundation work. Every task remains unchecked until performed and supported by
actual evidence.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Independent work in different files with no dependencies.
- **[Story]**: User-story label, such as US1, US2, or US3.
- Each task names the output path and requirement/criterion it supports.

## Phase 1: Setup

**Purpose**: Initialize the application, independent harness, and evidence record.

- [x] T001 Create the application, frontend, and validation directories from plan.md; initialize package files and `pyproject.toml` with FastAPI, Uvicorn, Jinja2, Pytest, HTTPX, Playwright, Ruff, and Bandit, placing validation tools in the `dev` extra used by quickstart.
- [x] T002 [P] Configure Pytest, Ruff, and Bandit in `pyproject.toml`; ensure the required harness path is included in Pytest discovery.
- [x] T003 [P] Create `harness-log.md` with NOT RUN / PENDING states and sections for exact commands, environment, actual outputs, failures, repairs, reruns, limitations, and human decision.
- [x] T004 [P] Create `validation/evidence/initial/README.md` and `validation/evidence/repaired/README.md` describing safe source snapshots and actual evidence manifests; prohibit credentials and fabricated outcomes.
- [x] T005 Document the initial configuration and run commands in `specs/001-ipo-deadline-tracker/quickstart.md`, including `IPO_ALERT_THRESHOLD` and the independent harness.

## Phase 2: Foundational Infrastructure

**Purpose**: Establish data persistence, application configuration, and a black-box harness before story implementation.

- [x] T006 Implement SQLite connection setup and schema initialization for the IPO table in `app/db/connection.py` and typed persistence records in `app/db/models.py`; use an isolated path supplied by `IPO_DATABASE_PATH` for validation runs.
- [x] T007 Implement repository CRUD methods in `app/db/repository.py` using bound parameters for every user-provided SQL value; preserve transaction integrity.
- [x] T008 Implement explicit application settings in `app/core/config.py`, including `IPO_ALERT_THRESHOLD` defaulting to 3, `IPO_DATABASE_PATH`, and errors for malformed or negative threshold values.
- [x] T009 Implement input validation and safe, consistent error handling in `app/utils/validation.py` and `app/core/errors.py`.
- [x] T010 Implement shared date and company-name normalization helpers in `app/utils/dates.py` and `app/utils/normalization.py`; define working days as weekdays strictly after closing, excluding weekends but not public holidays.
- [x] T011 Wire the FastAPI application, API router, web router, template directory, and static directory in `app/main.py` and `app/api/deps.py`.
- [x] T012 Create `validation/harness/conftest.py` to configure `IPO_DATABASE_PATH` for an isolated test database, start/use the application externally, expose an HTTP base URL and Playwright browser fixture, and ensure harness tests do not import modules from `app/`.
- [x] T013 [P] Add harness smoke and API contract checks for documented endpoints, status codes, response fields, and validation/error shapes in `validation/harness/test_api_contract.py`.

**Checkpoint**: The app can be started against an isolated SQLite database; the external harness can reach it and validate its documented contract.

## Phase 3: User Story 1 - Maintain IPO Records (Priority: P1, MVP)

**Goal**: Create, view, update, and delete valid IPO records without losing data or accepting duplicates.

**Independent Test**: Through the public API and UI, create a valid IPO; retrieve it; update it while preserving omitted optional dates; explicitly clear an optional date; reject invalid and duplicate records; cancel and confirm deletion.

### Independent Harness Tests

- [x] T014 [US1] Test valid IPO creation, list/detail retrieval, required/optional response fields, and timestamps through HTTP in `validation/harness/test_crud_and_validation.py` (FR-01, FR-05).
- [x] T015 [US1] Test empty company name, missing required dates, malformed dates, impossible calendar dates, and closing-before-opening rejection with exact safe error assertions in `validation/harness/test_crud_and_validation.py` (FR-02, FR-03, FR-04, FR-16, SC-002).
- [x] T016 [US1] Test update preservation for omitted optional fields, intentional clearing for explicitly empty fields, and invalid updated values through HTTP in `validation/harness/test_crud_and_validation.py` (FR-06, SC-002).
- [x] T017 [US1] Use Playwright to test rendered base/list/form/detail pages and CSS/JavaScript loading, and deletion confirmation in `validation/harness/test_ui_flows.py`: cancel sends no DELETE request; confirm deletes. Verify deleted and never-deleted historical record retrieval in `validation/harness/test_crud_and_validation.py` (FR-01, FR-05, FR-07, FR-15).
- [x] T018 [US1] Test controlled corrupted persisted date/field data and database read/write failures; assert safe explicit errors, no fabricated status, and no silent record rewrite in `validation/harness/test_corrupted_data.py` (FR-09, FR-16, SC-002).
- [x] T019 [US1] Test duplicate rejection through HTTP for case and whitespace variations, a clear conflict response, and non-duplicates when any key field differs in `validation/harness/test_crud_and_validation.py` (FR-14, SC-005).

### Implementation

- [x] T020 [US1] Define create, read, and partial-update request/response validation in `app/schemas/ipo.py`, distinguishing omitted fields from explicit empty optional dates (FR-01, FR-02, FR-03, FR-06).
- [x] T021 [US1] Implement safe, user-readable validation, duplicate, not-found, and corrupted-data errors in `app/core/errors.py` (FR-16).
- [x] T022 [US1] Implement IPO record create, view, update, and delete orchestration in `app/services/ipo_service.py`, preserving omitted optional values and rejecting invalid resulting records (FR-01, FR-05, FR-06, FR-07).
- [x] T023 [US1] Implement IPO CRUD API endpoints in `app/api/routes/ipos.py` with documented request/response codes and safe errors (FR-01, FR-05, FR-06, FR-07).
- [x] T024 [US1] Implement one duplicate identity comparator in `app/utils/normalization.py`, expose it through `app/services/duplicate_service.py`, and use it in the transaction-safe repository insert/update checks (FR-14).
- [x] T025 [US1] Implement the IPO list, form, detail, and shared layout in `frontend/templates/ipo_list.html`, `frontend/templates/ipo_form.html`, `frontend/templates/ipo_detail.html`, and `frontend/templates/base.html` (FR-01, FR-05, FR-06, FR-07).
- [x] T026 [US1] Implement form submission, validation display, explicit optional-date clearing, and delete confirmation behavior in `frontend/static/js/app.js` (FR-01, FR-02, FR-06, FR-07, FR-16).
- [x] T027 [US1] Implement responsive layout and distinct validation/confirmation states in `frontend/static/css/styles.css` (FR-05, FR-07, FR-16).
- [x] T028 [US1] Mount Jinja templates, web routes, CSS, and JavaScript through FastAPI in `app/web/routes.py` and `app/main.py`; verify the list, form, and detail routes are served (FR-01, FR-05, FR-07).
- [x] T029 [US1] Add SQLite constraints in `app/db/connection.py`, persisted-field validation in `app/db/models.py`, and transaction handling in `app/db/repository.py` for required fields and valid stored values (FR-02, FR-03, FR-04).

**Checkpoint**: US1 is independently validated through the public HTTP contract and user interface.

## Phase 4: User Story 2 - Understand Status and Deadline Urgency (Priority: P1)

**Goal**: Derive deterministic IPO status, countdown/expiry information, and approaching-deadline alerts.

**Independent Test**: Test immediately before, on, and after opening, closing, and listing; verify signed days, elapsed days, and alerts for zero, default, configured, and invalid thresholds.

### Independent Harness Tests

- [x] T030 [US2] Test status boundaries immediately before/on/after opening and closing, plus before/on/after listing, by creating valid records relative to the system's actual current date in `validation/harness/test_dates_and_alerts.py`; do not rely on application-module imports or clock mocks (FR-08, FR-09, SC-003).
- [x] T031 [US2] Test `days_remaining` as closing minus current date: future positive, closing-day zero, past negative; verify expired UI/API indicator and positive elapsed days without a positive countdown in `validation/harness/test_dates_and_alerts.py` (FR-10, SC-003).
- [x] T032 [US2] Test listing validation at and around the minimum date three weekdays strictly after closing, including Friday/weekend crossings and confirming every Monday-Friday date counts without holiday-calendar lookup, in `validation/harness/test_dates_and_alerts.py` (FR-02, FR-08, SC-002, SC-003).
- [x] T033 [US2] Test threshold default 3, configured positive values, threshold zero, inclusive alert boundaries, rejection of negative/non-integer settings, and expired-IPO exclusion in `validation/harness/test_dates_and_alerts.py` (FR-11, SC-003).

### Implementation

- [x] T034 [US2] Implement the explicit three-weekday-after-closing calculator and calendar-date parsing in `app/utils/dates.py`, skipping Saturday/Sunday and not excluding public holidays (FR-02, FR-08).
- [x] T035 [US2] Implement Upcoming/Open/Closed/Listed calculation with inclusive opening, closing, and listing boundaries in `app/services/status_service.py` (FR-08, FR-09).
- [x] T036 [US2] Implement signed `days_remaining` and positive `expired_days` derivation in `app/services/status_service.py`; expose both without storing them as permanent IPO values (FR-05, FR-10).
- [x] T037 [US2] Implement alert derivation using the validated application-wide threshold in `app/services/alert_service.py`; approaching applies only to Open IPOs within the inclusive 0-to-threshold range (FR-11).
- [x] T038 [US2] Include status, signed days, expired days, and alert state in API/list/detail presentation in `app/schemas/ipo.py`, `app/api/routes/ipos.py`, `frontend/templates/ipo_list.html`, and `frontend/templates/ipo_detail.html` (FR-05, FR-08, FR-10, FR-11).
- [x] T039 [US2] Display expired records as expired with elapsed calendar days, and approaching records with distinct alert styling, in `frontend/templates/ipo_list.html`, `frontend/templates/ipo_detail.html`, and `frontend/static/css/styles.css` (FR-10, FR-11).
- [x] T040 [US2] Document the no-public-holiday-calendar limitation in the UI/help text and `specs/001-ipo-deadline-tracker/quickstart.md` (FR-08, SC-006).

**Checkpoint**: US2 calculations and UI states match the tested boundary and threshold rules.

## Phase 5: User Story 3 - Find and Review IPO History (Priority: P2)

**Goal**: Search by company, filter by derived status, sort by opening/closing date, and retain historical records.

**Independent Test**: Create varied records; verify matching and no-match searches, each status filter, both date sort fields and directions, and retained historical records.

### Independent Harness Tests

- [x] T041 [US3] Test trimmed, case-insensitive company-name substring search with matches and no-match results through HTTP in `validation/harness/test_search_filter_sort.py` (FR-12, SC-004).
- [x] T042 [US3] Test each status filter against records in all supported statuses, including no-result filters, in `validation/harness/test_search_filter_sort.py` (FR-12, SC-004).
- [x] T043 [US3] Test opening/closing date sort in ascending and descending order and IPO-ID-ascending tie handling in `validation/harness/test_search_filter_sort.py` (FR-13, SC-004).
- [x] T044 [US3] Test historical records remain available until explicitly deleted, search/filter/sort do not mutate records, and SQL-like search text is safely treated as data in `validation/harness/test_search_filter_sort.py` (FR-12, FR-15, SC-004, SC-005).

### Implementation

- [x] T045 [US3] Implement trimmed, Unicode case-insensitive substring search and derived-status filtering in `app/services/ipo_service.py` without interpolating search text into SQL (FR-12).
- [x] T046 [US3] Implement allow-listed opening/closing date sort fields, ascending/descending order, and IPO-ID-ascending tie-breaker in `app/services/ipo_service.py` (FR-13).
- [x] T047 [US3] Add search, status filter, sort field, and sort direction parameters to `GET /api/ipos` and the list view in `app/api/routes/ipos.py` and `app/web/routes.py` (FR-12, FR-13).
- [x] T048 [US3] Add native GET search/filter/sort controls and empty-result states in `frontend/templates/ipo_list.html` and responsive styling in `frontend/static/css/styles.css` (FR-12, FR-13, FR-15).

**Checkpoint**: US3 is independently validated and does not change retained IPO records.

## Phase 6: Independent Validation, Evidence, and Acceptance

**Purpose**: Run all mandatory gates, preserve evidence, and obtain human accountability.

- [x] T049 Run the complete independent contract/integration harness with `python -m pytest validation/harness -q`; append the exact command, environment, actual output, and exit status to `harness-log.md` (FR-01â€“FR-16, SC-001â€“SC-005).
- [x] T050 Run Ruff with `python -m ruff check .` and Bandit with `python -m bandit -r app`; review tracked configuration/source for hardcoded credentials; record exact commands, actual outputs, review evidence, and exit statuses in `harness-log.md` (constitution security and quality gates).
- [x] T051 Before any repair, preserve the initial implementation snapshot and its actual harness/Ruff/Bandit evidence in `validation/evidence/initial/`; record snapshot identifiers and evidence paths in `harness-log.md`.
- [x] T052 For each repair, preserve the repaired implementation and repair evidence in `validation/evidence/repaired/`; rerun the exact same harness, Ruff, and Bandit command set and record failures, changes, and actual rerun outcomes in `harness-log.md`.
- [X] T053 Review known limitations, residual risks, evidence, and all FR/SC trace links; have a human reviewer record an explicit ACCEPT or REJECT decision, reviewer, date, and rationale in `harness-log.md` (SC-006).
- [x] T054 Update `specs/001-ipo-deadline-tracker/quickstart.md` only to match the verified commands and actual validation workflow; never write expected outcomes as executed results.

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) precedes foundational work.
- Foundation (Phase 2) blocks all stories.
- User stories require the foundation; the P1 CRUD and date-awareness stories
  should be delivered before the P2 search/history story.
- Final validation and human acceptance follow implementation and any repairs.

### Story Dependencies

- US1 is the MVP: record creation and CRUD are prerequisites for useful status
  display and record search.
- US2 depends on validated IPO records and application configuration.
- US3 depends on stored records and derived status calculations.

### Parallel Opportunities

- T002-T004 may be parallelized across configuration and documentation paths.
- Within US1, harness test files, schemas, presentation templates, and static
  assets can be developed in parallel after the harness foundation, provided
  shared files are not concurrently edited.
- US2 boundary and alert tests are in one harness file and are intentionally
  not marked parallel; calculation modules can be separated by service.
- US3 search/filter and sorting API behavior can be developed in parallel only
  after repository interfaces are agreed.
- The final Pytest, Ruff, and Bandit checks may run independently, but all
  outcomes must be recorded before human acceptance.

## Requirement and Success-Criterion Traceability

Each row names at least one implementation task and one independent validation
or review task. Tasks remain unchecked until actual work and evidence exist.

| Requirement | Implementation task(s) | Validation/review task(s) |
|---|---|---|
| FR-01 | T020, T022-T028 | T014 |
| FR-02 | T009-T010, T020, T029, T034 | T015, T032 |
| FR-03 | T009, T020-T021 | T015 |
| FR-04 | T009, T029 | T015 |
| FR-05 | T022-T023, T025, T038 | T014 |
| FR-06 | T020, T022, T026 | T016 |
| FR-07 | T022-T023, T025-T028 | T017 |
| FR-08 | T034-T035, T038, T040 | T030, T032 |
| FR-09 | T009, T021, T035 | T018, T030 |
| FR-10 | T036, T038-T039 | T031 |
| FR-11 | T008, T037-T039 | T033 |
| FR-12 | T045, T047-T048 | T041-T042 |
| FR-13 | T046-T048 | T043 |
| FR-14 | T010, T024 | T019 |
| FR-15 | T007, T022-T023, T048 | T017, T044 |
| FR-16 | T009, T021 | T015, T018-T019 |
| SC-001 | T022-T028 | T014, T049 |
| SC-002 | T009, T020-T021, T029, T034 | T015-T019, T032, T049 |
| SC-003 | T008, T034-T039 | T030-T033, T049 |
| SC-004 | T045-T048 | T041-T044, T049 |
| SC-005 | T007, T020-T024, T045 | T015-T019, T044, T049 |
| SC-006 | T003, T040, T051-T052 | T053 |

## Implementation Strategy

1. Complete setup and foundational tasks, including the independent HTTP
   harness, before story work.
2. Deliver US1 as the MVP and verify its CRUD, validation, duplicate, and
   confirmation behavior.
3. Add US2 deterministic date/status/alert behavior and verify all boundaries.
4. Add US3 search, filtering, sorting, and history review.
5. Run Pytest harness, Ruff, and Bandit; preserve actual evidence and rerun the
   same gates after repairs.
6. Do not record ACCEPT until a human reviewer has reviewed the evidence and
   limitations and entered a decision in `harness-log.md`.

