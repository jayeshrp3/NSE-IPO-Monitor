# Research: IPO Deadline Tracker Decisions

## Decision 1: Deterministic date logic

**Decision**: IPO status, days remaining, and alert state will be derived in service-layer functions from the current system date and validated IPO dates.

**Rationale**: This aligns with the constitution’s requirement for deterministic calculations and the specification’s requirement to avoid silent status assignment when data is invalid or incomplete.

**Alternatives considered**:
- Storing status as a permanent database field was rejected because it can drift from the actual current date and creates hidden inconsistency.
- Using a third-party library for date logic was rejected as unnecessary for a small deterministic application.

## Decision 2: Listing-date rule

**Decision**: A listing date, when provided, must be on or after the date three working days strictly after closing. Working days are Monday through Friday; weekends are skipped and public holidays are not excluded.

**Rationale**: This resolves the business ambiguity without widening project scope and keeps status evaluation consistent and auditable. The lack of public-holiday exclusion is an explicit Part 1A limitation.

**Alternatives considered**:
- Allowing any listing date after opening was rejected because it would reduce the determinism and clarity of the flow.
- Treating listing as optional and unrestricted was rejected because it weakens validation and can produce false status transitions.

## Decision 3: Duplicate detection policy

**Decision**: Duplicate records are rejected when normalized company name plus opening and closing dates match. Normalize by trimming leading/trailing whitespace, collapsing repeated internal whitespace, and case-folding for comparison.

**Rationale**: This matches the approved specification and prevents near-duplicate entries from being saved under different capitalization or spacing variations.

**Alternatives considered**:
- Duplicate-by-company-name-only was rejected because multiple IPOs for the same company on different dates would be incorrectly treated as duplicates.
- Duplicate-by-opening-date-only was rejected because companies can have multiple offerings over time.

## Decision 4: Alert threshold behavior

**Decision**: Read the application-wide `IPO_ALERT_THRESHOLD` setting as a non-negative integer, defaulting to 3 calendar days. Reject malformed or negative configuration explicitly. The alert fires only when the IPO is Open and days remaining are between 0 and the threshold, inclusive.

**Rationale**: This matches the approved rule and avoids misclassifying expired IPOs as approaching deadlines.

**Alternatives considered**:
- Triggering alerts for all past-due records was rejected because it would obscure true urgency.
- Allowing a negative threshold was rejected because threshold values must be non-negative integers.

## Decision 5: Optional date semantics

**Decision**: The system distinguishes omitted optional date fields from explicit empty values. Omitted fields preserve the existing value; empty values clear it intentionally.

**Rationale**: This preserves user data and supports a clear update contract without data loss.

**Alternatives considered**:
- Treating empty values as “no change” was rejected because it prevents users from intentionally clearing optional dates.
- Treating all missing values as deletions was rejected because it can cause unintentional data loss.

## Decision 6: Frontend scope

**Decision**: A lightweight server-rendered UI using HTML, CSS, and Bootstrap is chosen over a separate JavaScript-heavy frontend framework.

**Rationale**: The project is small, deterministic, and specification-driven. This keeps implementation simpler and more auditable while still satisfying the frontend requirement.

**Alternatives considered**:
- React or Vue was rejected because the scope does not justify a more complex frontend architecture.
- Pure API-only delivery was rejected because the requirement explicitly calls for a web UI and user-facing IPO management workflow.

## Decision 7: SQLite access

**Decision**: Use Python's standard-library `sqlite3` module, with SQL isolated
in the repository layer and all user-provided values bound as query parameters.

**Rationale**: The Part 1A data model is a single table without a need for ORM
relationships. The standard library avoids an unnecessary runtime dependency
while preserving the required separation between persistence and business
logic.

**Alternatives considered**:
- SQLAlchemy was not selected because the current scope does not benefit from
  ORM mapping or migration abstractions enough to justify the extra dependency.

## Decision 8: Independent validation and evidence

**Decision**: Mandatory acceptance and contract/integration checks are
implemented in `validation/harness/` and exercise the public HTTP contract
without importing application modules. Use an isolated test database and
configured base URL. Record actual runs and human decisions in `harness-log.md`;
preserve initial and repaired implementation evidence and rerun the same checks
after repairs.

**Rationale**: This satisfies the constitution's independence, traceability,
failure-evidence, and human-accountability requirements.

**Alternatives considered**:
- Importing application internals in mandatory tests was rejected because it
  couples the acceptance oracle to the implementation being evaluated.
