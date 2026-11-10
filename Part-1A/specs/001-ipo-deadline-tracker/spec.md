# Feature Specification: IPO Deadline Tracker

**Feature Branch**: `[001-ipo-deadline-tracker]`

**Created**: 2026-11-10

**Status**: Draft

**Input**: User description: "Create a detailed functional specification for the project NSE IPO Monitoring & Deadline Alert System – Part 1A."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Maintain IPO records with confidence (Priority: P1)

An individual investor wants to add IPO records for companies and keep an accurate, reviewable list of upcoming or recent offerings. The user must be able to add, view, update, and delete records while receiving clear validation feedback when data is missing or invalid.

**Why this priority**: This is the core user value of the product: maintaining a reliable personal IPO watchlist with trustworthy data and consistent status calculations.

**Independent Test**: A user can create a valid IPO record, review it in the saved list, and then edit or delete it without losing unrelated data or creating invalid statuses.

**Acceptance Scenarios**:

1. **Given** the user is creating a new IPO record, **When** they provide a valid company name and valid opening and closing dates, **Then** the record is saved and appears in the list with a computed status and remaining days.
2. **Given** the user submits a record with a missing company name or an invalid date, **When** the system validates the submission, **Then** it rejects the record and explains the specific problem.
3. **Given** an IPO exists and the user edits one field, **When** they save an update without changing optional fields, **Then** the previous values remain intact unless explicitly modified.
4. **Given** a record exists with the same normalized company name, opening date, and closing date, **When** the user submits it again, **Then** the system rejects it with a clear duplicate-record error.
5. **Given** an IPO has optional milestone dates, **When** the user omits an optional field while updating, **Then** its value is preserved; **When** the user submits that field explicitly empty, **Then** its value is cleared.

---

### User Story 2 - Understand IPO status and deadline urgency (Priority: P1)

A user wants to know whether an IPO is upcoming, open, closed, or listed, and whether the closing date is approaching or already expired. The system must calculate status and remaining days deterministically and highlight deadlines that require attention.

**Why this priority**: The product's value depends on accurate, understandable deadline awareness; misleading status or inconsistent date math would reduce trust and harm decision-making.

**Independent Test**: A user can review a list of IPO records and clearly distinguish between active offerings, passed deadlines, and upcoming events without ambiguity or hidden assumptions.

**Acceptance Scenarios**:

1. **Given** an IPO whose opening date is in the future, **When** the system evaluates the dates, **Then** it marks the IPO as Upcoming and shows the remaining time until closing.
2. **Given** an IPO whose opening and closing dates span the current date, **When** the system evaluates the current date, **Then** it marks the IPO as Open.
3. **Given** an IPO whose closing date has passed, **When** the system evaluates the date, **Then** it marks the IPO as Closed or Listed according to the predefined rule set and labels the deadline as expired.
4. **Given** a deadline is within the configured alert threshold, **When** the system renders the list, **Then** it highlights the record as approaching and distinguishes it from expired deadlines.

---

### User Story 3 - Search, sort, and manage historical IPO data (Priority: P2)

A user wants to find specific companies, narrow results by IPO status, and sort the list by date fields without losing historical records. The system must retain past IPO data until the user explicitly removes it and handle duplicate or malformed entries safely.

**Why this priority**: Search and sorting improve usability and allow users to monitor multiple IPOs efficiently, while historical retention keeps a reliable audit trail of past offerings.

**Independent Test**: A user can filter the IPO watchlist by company name or status, then sort by opening or closing date and delete selected records after confirmation.

**Acceptance Scenarios**:

1. **Given** multiple IPO records exist, **When** the user searches for a company name, **Then** only matching records are shown.
2. **Given** records have varying statuses, **When** the user filters by status, **Then** the system shows only records in that category.
3. **Given** multiple IPO records are sorted by closing date, **When** the user chooses sorting, **Then** the list order follows the selected date criteria consistently.
4. **Given** historical IPO records exist, **When** the user views the list without deleting them, **Then** those records remain available alongside current records.

---

### Edge Cases

- What happens when the closing date is earlier than the opening date?
- What happens when a required date is missing or malformed?
- What happens when the current date is exactly equal to an IPO opening, closing, or listing boundary?
- What happens when a user tries to save an IPO that already exists with the same normalized company name, opening date, and closing date?
- What happens when optional allotment, refund, or listing dates are left blank after an earlier record had values?
- What happens when the configured alert threshold is set to zero or a negative value?
- What happens when data is manually edited to remove previously saved values or contains corrupted date text?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-01**: The system MUST allow a user to add an IPO record with a company name, opening date, and closing date, and optional allotment, refund, and listing dates.
- **FR-02**: The system MUST validate all required and optional date inputs before saving an IPO record.
- **FR-03**: The system MUST reject an IPO record when the company name is empty or when date values are missing, invalid, or malformed.
- **FR-04**: The system MUST reject a record when the closing date is earlier than the opening date.
- **FR-05**: The system MUST allow a user to view all saved IPO records including company name, opening date, closing date, optional dates, IPO status, and days remaining.
- **FR-06**: The system MUST allow a user to edit an existing IPO record and preserve any unchanged optional values unless the user explicitly modifies them.
- **FR-07**: The system MUST allow a user to delete an IPO record only after the web UI obtains explicit confirmation; canceling confirmation MUST send no delete request. Historical records MUST NOT be removed without explicit user action.
- **FR-08**: The system MUST calculate IPO status using predefined deterministic date rules and must classify each record as Upcoming, Open, Closed, or Listed when required dates are valid.
- **FR-09**: The system MUST not silently assign a status when required dates are missing or invalid; instead, it MUST surface the invalid or incomplete condition clearly.
- **FR-10**: The system MUST calculate the number of days remaining until the IPO closing date based on the system's current date and must handle past closing dates correctly.
- **FR-11**: The system MUST highlight IPOs approaching their closing date based on a configurable, non-negative integer threshold, defaulting to 3 calendar days. The threshold MUST be loaded from application configuration; invalid or negative values MUST be rejected with a clear configuration error. The alert MUST apply only to Open IPOs whose days remaining are from 0 through the threshold, inclusive, and MUST clearly distinguish expired deadlines from upcoming deadlines.
- **FR-12**: The system MUST support trimmed, case-insensitive substring search by company name and filtering by IPO status.
- **FR-13**: The system MUST support sorting IPO records by opening date or closing date; equal sort dates MUST use IPO ID ascending as a stable tie-breaker.
- **FR-14**: The system MUST reject a duplicate IPO submission when its normalized company name, opening date, and closing date match an existing record, and MUST return a clear duplicate-record error.
- **FR-15**: The system MUST preserve historical IPO records unless the user explicitly deletes them.
- **FR-16**: The system MUST provide clear human-readable error messages for validation failures, duplicate entries, and corrupted data conditions.

### Business Rules

- A company name MUST be present and non-empty before an IPO can be saved.
- Opening and closing dates are mandatory for a valid IPO record.
- Optional dates may be left blank if not available, but if provided they MUST be valid calendar dates.
- The system MUST apply a consistent, documented set of date-boundary rules for status calculation.
- `days_remaining` MUST be the signed calendar-day difference `closing_date - current_date`: positive before closing, zero on closing, and negative after closing. For display after closing, the system MUST show an expired indicator and the positive number of elapsed calendar days; it MUST NOT present a positive countdown.
- The default alert threshold MUST be 3 calendar days. The application MUST load a configurable non-negative integer threshold from application configuration and reject invalid or negative values.
- An approaching-deadline alert MUST be active only when status is Open and `days_remaining` is between zero and the configured threshold, inclusive. Expired IPOs MUST NOT be approaching.
- Historical records MUST remain stored until explicitly removed by the user.
- A valid status MUST reflect the date logic only when the required date inputs are present and valid.

### IPO Status and Date-Boundary Rules

- **Upcoming**: status MUST be Upcoming when the current date is before the opening date.
- **Open**: status MUST be Open when the current date is on or after the opening date and on or before the closing date.
- **Closed**: status MUST be Closed when the current date is after the closing date and either no listing date is available or the listing date is still in the future.
- **Listed**: status MUST be Listed when the current date is on or after the listing date.
- **Boundary inclusion**: the opening date is included in the Open period, the closing date is included in the Open period, and the listing date is included in the Listed period.
- **Boundary tests**: automated tests MUST evaluate the current date immediately before, on, and after opening, closing, and listing dates.
- **Listing-date validation**: when a listing date is provided, it MUST be on or after the date reached by counting three working days after the closing date. The closing date is not counted. Working days are Monday through Friday; Saturdays and Sundays are excluded, and public holidays are not excluded. The rule MUST be enforced consistently in validation and status calculation.
- **Working-day limitation**: Part 1A does not use an NSE, Indian, or other public-holiday calendar. A weekday that is a public holiday still counts as a working day for this calculation. This limitation MUST be documented to users and reviewers.

### Days Remaining and Alerts

- Days remaining MUST be calculated as closing date minus current date in calendar days.
- On the closing date, the system MUST display 0 days remaining.
- After the closing date, the system MUST display an expired indicator and the number of days elapsed rather than a misleading positive countdown.
- The default alert threshold MUST be 3 calendar days.
- The alert threshold MUST be read from application configuration as a non-negative integer; if absent it defaults to 3, and invalid or negative configuration MUST fail explicitly.
- The system MUST trigger an approaching-deadline alert only when the IPO is Open and the days remaining are between 0 and the configured threshold, inclusive.
- Expired IPOs MUST NOT be classified as approaching deadlines.
- Derived `alert_status` MUST be `Expired` when the closing date has passed, `Approaching` only when the IPO is Open and within the configured threshold, and `None` otherwise.
- Company-name search MUST trim the query and perform a case-insensitive substring match.
- Date sorting MUST use the selected date field and use IPO ID ascending as a stable tie-breaker.

### Duplicate Handling and Name Normalization

- Records MUST be treated as duplicates when the normalized company name and the opening and closing dates are identical.
- Company-name normalization for duplicate comparison MUST trim leading and trailing whitespace, collapse repeated internal whitespace to a single space, and compare case-insensitively using case folding. No other punctuation or legal-suffix normalization is implied.
- Duplicate submissions MUST be rejected with a clear message identifying that a record with the same normalized name and opening/closing dates already exists.

### Optional Date Update Semantics

- Users MUST be allowed to intentionally clear optional dates.
- When an update request omits an optional date field, the existing value MUST be preserved.
- When an update request explicitly sends an empty value for an optional date field, the system MUST treat that as an intentional clear and MUST store the field as blank.
- The system MUST distinguish between omitted optional fields and explicitly cleared optional fields during update validation and persistence.

### Scope Limitations

- Part 1A does not integrate a live NSE API; records are manually entered or sample historical data.
- Part 1A does not provide buying or selling of shares, trading, or payment processing.
- AI-based announcement extraction belongs to Part 1B and is not included here.
- Listing-date working-day calculation does not exclude public holidays; this limitation MUST be disclosed in the UI and project documentation.

### Key Entities

- **IPO Record**: Represents one offering with a company name, required opening and closing dates, optional allotment, refund, and listing dates, a computed status, and derived remaining-day information.
- **User**: Represents the end user who adds, reviews, edits, filters, and removes IPO records.
- **Alert Threshold**: Represents the configurable rule that determines when the system highlights an IPO as approaching its deadline.
- **Historical Record**: Represents retained IPO data that remains available unless the user explicitly deletes it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create and save a valid IPO record in a single workflow without needing to understand the internal status rules.
- **SC-002**: Automated validation tests cover all invalid-input and boundary conditions for required fields, malformed dates, duplicate records, and date-sequence validation, and each failure produces the correct user-facing error.
- **SC-003**: Automated tests confirm that the system consistently calculates IPO status and days remaining for all valid records using the same current-date rule set across repeated checks.
- **SC-004**: Automated tests confirm that users can find and review a record by company name, status, or date ordering without manual inspection of the entire dataset.
- **SC-005**: Automated tests confirm that the application rejects invalid input and duplicate records before they are saved, preventing inconsistent or corrupted data.
- **SC-006**: A human reviewer can inspect the stored records and trace each status, deadline alert, and duplicate rejection to the approved business rules without guessing at hidden logic.

### Acceptance Criteria Verification

- Every functional requirement MUST map to at least one implementation task and at least one automated validation task in the feature task list. Tasks MUST reference the requirement identifiers to preserve traceability.
- Required date validation MUST be verified by tests covering empty values, malformed inputs, invalid sequences, and valid records.
- Listing-date validation MUST be verified by tests that reject a listing date earlier than the date three Monday-to-Friday weekdays after closing and accept a listing date on that minimum date. Weekend days are skipped; public holidays are counted as weekdays.
- IPO status rules MUST be verified by tests covering dates immediately before, on, and after the opening date, closing date, and listing date.
- Days remaining MUST be verified by tests for future closing dates, closing today, and past closing dates. Past dates MUST expose a negative signed difference, an expired indicator, and positive elapsed days in the user-facing representation.
- Duplicate rejection MUST be verified by tests for matching opening/closing dates with case and whitespace variants, a clear duplicate error, and non-duplicates where any of the three key fields differs.
- Alert threshold behavior MUST be verified by tests for the default of 3, configured values, invalid and negative configuration, thresholds of zero, inclusion at both range boundaries, and expired-record exclusion.
- Optional-date update semantics MUST be verified by tests for omitted field preservation, explicit clearing, and invalid date rejection.
- Deletion confirmation MUST be verified by testing that canceling the UI confirmation does not send a delete request and confirming it deletes the record.
- Corrupted data handling MUST be verified with controlled integration tests that inject malformed persisted values and confirm the application surfaces a safe error without assigning a fabricated status or silently altering records.
- Search, status filtering, and opening/closing date sorting MUST each have positive, negative/no-match, and ordering tests.
- Search MUST be verified with case differences, surrounding query whitespace, and no-match input. Sort ties MUST be verified against the IPO ID ascending tie-breaker.
- All acceptance tests MUST run through an independent validation harness that does not import application implementation modules. The harness MUST record actual commands, results, failures, repair attempts, and reruns in `harness-log.md`; no outcome may be reported as PASS without execution evidence.
- The same harness checks MUST be rerun after repairs. Initial and repaired implementation evidence MUST be preserved, and a human reviewer MUST record a final ACCEPT or REJECT decision with the evidence reviewed.

## Assumptions

- Users are managing a personal watchlist rather than a shared enterprise system.
- The initial data source is manually entered or sample historical IPO data, not live NSE API data.
- The system will operate in a deterministic, single-user or small-user context where consistent date calculations are more important than live market synchronization.
- The alert threshold is configurable through application configuration; its default is 3 and its only numeric constraint is that it be a non-negative integer.
- Working days mean Monday through Friday; public holidays are not excluded because Part 1A does not integrate a holiday calendar.
- Historical records must be retained unless explicitly deleted by the user or an administrator action is taken.
- No payment, trading, or real-money action is part of the Part 1A scope.
- A listing date, when provided, must be on or after the date reached by counting three Monday-to-Friday working days strictly after closing; weekends are excluded and public holidays are not.
