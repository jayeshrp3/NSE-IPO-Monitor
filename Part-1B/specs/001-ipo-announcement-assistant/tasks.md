# Tasks: AI-Powered IPO Announcement & Deadline Assistant

**Input**: Design documents from `/specs/001-ipo-announcement-assistant/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`

**Testing**: Test-first development is required by the Part 1B constitution. Write each requirement-linked test before its implementation and verify the test fails for the expected reason.

**Organization**: Tasks are grouped by setup, shared foundation, then user story priority. Evaluation remains independent of application code.

## Format

Every task follows `- [ ] T### [P?] [Story?] Description with exact file path(s)`.
`[P]` marks tasks that can proceed in parallel. Story labels are required for user-story phases.

## Phase 1: Setup

**Purpose**: Establish the local Python web application and validation tooling.

- [x] T001 Create the `app/`, `evaluation/`, `tests/unit/`, `tests/contract/`, and `tests/integration/` package directories with package markers where needed.
- [x] T002 Configure Python 3.11+ project metadata and only the planned local dependencies in `pyproject.toml`.
- [x] T003 [P] Configure pytest and Ruff settings in `pyproject.toml`.
- [x] T004 [P] Add local-only configuration example for Ollama endpoint, model name, and a 50,000-character announcement limit in `.env.example`; exclude real secrets and local environment files in `.gitignore`.

## Phase 2: Foundational

**Purpose**: Build shared contract and evaluation foundations before user-story implementation.

- [x] T005 Add contract tests for strict schema version, required top-level and field-result members, distinct company/date value constraints, ISO calendar-date format, status/value consistency, warning/evidence/error schemas, validation-check enums, and rejection of extra properties and invalid model output in `tests/contract/test_extraction_schema.py`.
- [x] T006 Add unit tests for date-field invariant outcomes: valid supported dates pass only when calendar-valid and chronology-compliant; impossible dates require null/`invalid`; missing source dates do not fail; ambiguous/conflicting/unsupported dates require null and the matching status; incorrect verified dates fail; and valid-source-date omission is scored by extraction accuracy rather than date invariants, in `tests/unit/test_date_validation.py`.
- [x] T007 [P] Add evaluation-manifest integrity tests requiring exactly E-01 through E-20, unique IDs, required input/setup, expected output/behavior, requirement references, and pass criteria in `tests/unit/test_evaluation_manifest.py`.
- [x] T008 [P] Add evaluation metric tests for field accuracy numerator/denominator/percentage and FR-024 date-invariant check applicability/pass rules covering valid, impossible, missing, ambiguous, conflicting, unsupported dates and chronology violations; calculate passed/applicable checks and percentage, test zero-denominator failure, and test four-dimension rubric aggregation in `tests/unit/test_evaluation_metrics.py`.
- [x] T009 Define version-1.0 Pydantic request, response, company-field, date-field, warning, validation-check, and typed API-error models matching `contracts/openapi.yaml`; enforce status/value consistency, real calendar dates, null unresolved values, and strict extra-field rejection in `app/schemas/extraction.py`.
- [x] T010 Implement deterministic date parsing, calendar/source verification and chronology validation independent of AI output; expose per-date-field and applicable chronology results to the application, while keeping harness FR-024 scoring independently recomputed from fixed case expectations and outputs, in `app/services/validation.py`.
- [x] T011 Create the fixed independent evaluation manifest with all 20 complete case fixtures E-01–E-20 from `specs/001-ipo-announcement-assistant/data-model.md` in `evaluation/cases.json`. Each case MUST retain its own exact input or controlled setup, expected field values/states or expected behavior, requirement links, applicable scoring flags, and case-specific criteria; E-18 remains present if comparison is deferred.
- [x] T012 Implement independent manifest loading, FR-024 applicability/pass calculation, other metric calculation, and case-result serialization in `evaluation/harness.py`; recompute evaluation outcomes from fixed case expectations and application outputs without importing application extraction/validation logic as the oracle.
- [x] T013 Verify and record the 20-case manifest-integrity and metric tests pass, including FR-024 numerator/denominator construction and correct safe-handling pass outcomes for E-12, E-13, and E-19, in `tests/unit/test_evaluation_manifest.py` and `tests/unit/test_evaluation_metrics.py`.

**Checkpoint**: Contracts, independent validators, and fixed evaluation suite are ready. User-story implementation must proceed test-first.

## Phase 3: User Story 1 - Extract and review an IPO announcement (Priority: P1) — MVP

**Goal**: Accept English announcement text and return a validated, transparent, versioned extraction through the local interface.

**Independent Test**: With a local Ollama model available, analyze a complete announcement and verify exact supported facts, schema version, summary, field evidence/status, and independent validation. Repeat with missing and ambiguous dates; verify nulls and warnings. Verify unavailable Ollama and invalid model output are surfaced without fallback or false success.

### Tests for User Story 1 (write and run before implementation)

- [x] T014 [P] [US1] Add API contract tests for `POST /api/v1/analyze`, separate `AnalysisResponse`/`ApiError` shapes, schema version, and blank, 50,000-character boundary, and over-limit request behavior (reject over-limit input before inference without truncation) in `tests/contract/test_analyze_api.py`.
- [x] T015 [P] [US1] Add extraction service tests for source-supported company/date fields, missing values, ambiguity, conflict, and grounded summary behavior in `tests/unit/test_extraction_service.py`.
- [x] T016 [P] [US1] Add UI-flow integration tests for submit, loading, result display, warnings, and invalid-result display in `tests/integration/test_analysis_ui.py`.
- [x] T017 [P] [US1] Add local Ollama adapter tests for unavailable service, timeout, malformed JSON, and no remote fallback in `tests/unit/test_ollama_client.py`.

### Implementation for User Story 1

- [x] T018 [US1] Implement local-only Ollama HTTP client with configured loopback endpoint, model selection, explicit timeout/unavailable errors, and no cloud fallback in `app/services/ollama_client.py`.
- [x] T019 [US1] Implement bounded extraction prompt construction, strict model response parsing and Pydantic validation against the planned `AnalysisResponse` fields, and source-evidence/status mapping in `app/services/extraction.py`; reject invalid or unexpected model output without returning a successful result.
- [x] T020 [US1] Implement `POST /api/v1/analyze` request handling, reject announcement text over 50,000 characters before inference without truncation, map success only to `AnalysisResponse`, map failures to typed `ApiError`, and preserve explicit validated response mapping in `app/api/routes.py`.
- [x] T021 [US1] Implement FastAPI startup and static/template mounting for the local web interface in `app/main.py`.
- [x] T022 [P] [US1] Implement the announcement input, submission state, and accessible result/warning/validation display in `app/templates/index.html`.
- [x] T023 [P] [US1] Implement browser submission and rendering for extracted facts, field states, summary, schema version, warnings, and validation status in `app/static/app.js`.
- [x] T024 [P] [US1] Add responsive minimal local styling for input, results, warnings, and validation state in `app/static/styles.css`.
- [x] T025 [US1] Run the US1 contract, unit, and integration tests and record results in `evaluation/evidence/initial/`; repair failures without weakening expected behaviors.

**Checkpoint**: US1 is independently usable with no comparison feature and no unsupported date presented as verified.

## Phase 4: User Story 2 - Inspect warnings and resist hostile announcement instructions (Priority: P1)

**Goal**: Preserve task boundaries for untrusted input and safely report prompt injection, invalid dates, unsupported language, unrelated content, and model errors.

**Independent Test**: Run E-09 through E-17, E-19, and E-20 against the application and verify no hostile or unsupported content overrides the extraction task; all failures, uncertainty, and validation outcomes are explicit.

### Tests for User Story 2 (write and run before implementation)

- [x] T026 [P] [US2] Add tests for source/task separation and prompt-injection content before, inside, and after IPO facts in `tests/unit/test_prompt_safety.py`.
- [x] T027 [P] [US2] Add API/integration tests for injection warnings, unrelated text, impossible dates, unsupported English-only scope, and safe invalid-output handling in `tests/integration/test_safety_cases.py`.
- [x] T028 [P] [US2] Add evaluation-case assertions that E-15 and E-20 pass only when hostile instructions are ignored and non-English extraction is not marked verified in `tests/unit/test_safety_evaluation.py`.
- [x] T051 [P] [US2] Add and execute the FR-025 browser/UI integration test in `tests/integration/test_ui_safe_rendering.py`. Inject HTML/script tags, event-handler attributes, malicious markup, and prompt-injection strings through announcement text and model-derived company/date values, summaries, evidence, and warnings. Assert all content is rendered as literal text (not interpreted as HTML/instructions), script and event handlers do not execute, untrusted content cannot alter DOM structure/attributes/controls, and expected application controls remain usable.

### Implementation for User Story 2

- [x] T029 [US2] Harden task instructions and isolate announcement text as untrusted source data in `app/services/extraction.py`; constrain output to the required schema and task.
- [x] T030 [US2] Add safe injection detection/reporting without treating announcement instructions as executable commands in `app/services/extraction.py`.
- [x] T031 [US2] Add English-only input handling and explicit unsupported-language response in `app/services/extraction.py` and `app/api/routes.py`.
- [x] T032 [US2] Ensure invalid calendar dates, chronology conflicts, model refusal, malformed output, and inference failures are displayed as unverified/failed rather than successful facts in `app/services/validation.py` and `app/api/routes.py`.
- [x] T052 [US2] After T051, implement FR-025 in `app/static/app.js`: render announcement-derived evidence, extracted values, summaries, and warnings only as inert text with safe DOM APIs; never interpret them as HTML or executable instructions, and preserve protected UI structure, attributes, and controls.
- [x] T033 [US2] After T029–T032 and T052, run E-01–E-17, E-19, and E-20 through the independent harness and retain initial failures and per-case evidence in `evaluation/evidence/initial/`; do not remove or alter any case or threshold.

**Checkpoint**: Security and uncertainty cases pass their fixed expected outcomes; failures remain visible in evidence.

## Phase 5: User Story 3 - Compare against a manually entered record (Priority: P2; secondary/deferrable)

**Goal**: When feasible without threatening core completion, compare extraction values with a manually entered Part 1A record without writes or database coupling.

**Independent Test**: For E-18, verify matching/differing/unavailable fields and that neither side changes. If this secondary feature is deferred, record the deferral and E-18 disposition while retaining E-18 in the fixed suite.

### Tests for User Story 3 (write and run before implementation)

- [ ] T034 [P] [US3] Add comparison tests for matching, differing, unavailable, invalid, and unverified extracted fields in `tests/unit/test_comparison.py`.
- [ ] T035 [P] [US3] Add manual comparison form and display integration tests for E-18 in `tests/integration/test_comparison_ui.py`.

### Implementation for User Story 3

- [ ] T036 [US3] Implement an in-memory manual comparison record and per-field comparison outcomes without persistence or Part 1A database access in `app/services/comparison.py`.
- [ ] T037 [US3] Add optional comparison input/output to the local UI without changing the extraction workflow in `app/templates/index.html` and `app/static/app.js`.
- [ ] T038 [US3] Record whether E-18 comparison is implemented or deferred and verify its corresponding criteria without removing E-18 from `evaluation/cases.json` in `evaluation/evidence/final/`.

**Deferral rule**: If US3 threatens completion of extraction, independent validation, or evaluation, defer T036–T037 and record the decision through T038. E-18 remains in the suite and all core gates remain mandatory.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Execute the full frozen evaluation, preserve repair history, and prepare human review.

- [x] T039 [P] Freeze scoring instructions for factual grounding, completeness, concise relevance, and uncertainty handling in `evaluation/rubric.md`, preserving the four equal weights and 0/0.5/1 anchors from FR-022.
- [ ] T040 Record and freeze the final evaluation configuration in `evaluation/evidence/final/evaluation-config.json` before the final evaluation starts. Include every constitution threshold (100% schema validity, 100% date-invariant compliance, zero invented dates, at least 90% field accuracy, at least 85% summary/uncertainty quality, and 100% prompt-injection safe handling); the complete fixed dataset E-01–E-20; Ollama model name/version and relevant settings; and evaluation methodology, including FR-024 date-field/chronology check applicability, pass/fail rules, formula, numerator/denominator reporting, nonzero-denominator rule, and all other metric and scoring rules. Do not change this configuration after observing final results.
- [x] T041 Run the unchanged E-01–E-20 suite before repairs and preserve model/configuration, every case result, each applicable date-invariant check result, aggregate metrics, and failures in `evaluation/evidence/initial/`.
- [ ] T042 Assign and preserve the four rubric scores (factual grounding, completeness, concise relevance, uncertainty handling; each 0, 0.5, or 1) for every applicable case from the initial E-01–E-20 run in `evaluation/evidence/initial/rubric-scores.json` before final evaluation; record per-case totals and aggregate percentage as `100 × awarded rubric points / available rubric points`.
- [x] T043 For each failure, record linked repair rationale and evidence in `evaluation/evidence/repairs/` without changing the case set, expected outcomes, metrics, scoring rules, or thresholds.
- [ ] T044 Rerun the same E-01–E-20 suite after repairs and preserve final configuration, per-case results, and each applicable date-invariant check result in `evaluation/evidence/final/`.
- [ ] T045 Assign and record the four rubric scores (factual grounding, completeness, concise relevance, uncertainty handling; each 0, 0.5, or 1) for every applicable final evaluation case in `evaluation/evidence/final/rubric-scores.json` before aggregate report generation. Preserve each case's four dimension scores and case total, then calculate aggregate quality as `100 × awarded rubric points / available rubric points`.
- [ ] T046 Generate the final evaluation report for all 20 cases in `evaluation/harness.py` and preserve it in `evaluation/evidence/final/`. Include exact field-accuracy and FR-024 date-invariant numerator/denominator/percentage, per-check date-invariant results, the case-level scores from `evaluation/evidence/final/rubric-scores.json`, schema results, prompt-injection outcomes, and aggregate quality.
- [ ] T047 Verify final gates: 100% schema validity, 100% date-invariant compliance calculated as FR-024 applicable checks passed/total applicable checks (nonzero denominator), zero invented dates, at least 90% field accuracy, at least 85% summary/uncertainty quality, and 100% prompt-injection safe handling. Confirm invalid-date and chronology-violation cases pass only when correctly detected/reported and affected dates are not verified; report numerator, denominator, percentage, and any failures in `evaluation/evidence/final/`.
- [ ] T048 Run all automated tests and the local end-to-end scenarios documented in `specs/001-ipo-announcement-assistant/quickstart.md`; retain output in `evaluation/evidence/final/`.
- [ ] T049 Record human reviewer findings, known limitations, and explicit ACCEPT or REJECT decision in `evaluation/evidence/final/human-review.md`.
- [x] T050 [P] Update local setup and user instructions for Ollama-only operation, supported English input, validation states, and evaluation commands in `README.md`.

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no prerequisites.
- Foundational (Phase 2) depends on setup and blocks all user-story implementation.
- US1 (Phase 3) depends on the foundation and is the MVP.
- US2 (Phase 4) depends on the US1 extraction/API boundary and adds security/uncertainty guarantees.
- US3 (Phase 5) depends on US1 output and is optional/deferrable; E-18 remains required in all cases.
- Polish/final evaluation (Phase 6) depends on US1 and US2. US3 may be explicitly deferred; final suite still includes all 20 cases.

### User Story Dependencies

- **US1**: Starts after Phase 2; no dependency on another user story.
- **US2**: Builds on the extraction boundary from US1.
- **US3**: Builds on US1 output; may be deferred without blocking core acceptance.

### Parallel Opportunities

- T003 and T004 can run in parallel after T001/T002 as applicable.
- T005–T008 test files can be authored in parallel; implementation T009–T012 follows those tests.
- T014–T017 test files can be authored in parallel before US1 implementations.
- T022–T024 UI artifacts can proceed in parallel once the API response shape is fixed.
- T026–T028 safety test files can be authored in parallel.
- T051 can be authored in parallel with T026–T028; T052 depends on T051 and must pass its safe-rendering assertions before US2 is considered complete.
- T034–T035 comparison tests can proceed in parallel if comparison is selected.
- T039 and T049 can be prepared in parallel with implementation, but rubric instructions and T040's complete configuration freeze must be completed before final evaluation.
- T042 follows T041 and assigns case-level scores before final evaluation; T045 repeats scoring for final outputs from T044 before report generation.
- T044 depends on T040 and the completed repair work T043; T045 depends on T044; T046 depends on T040 and T045.
- T047 follows T046 and evaluates the report against unmodified thresholds.

### Parallel Example: User Story 1

```text
Write first: tests/contract/test_analyze_api.py
Write first: tests/unit/test_extraction_service.py
Write first: tests/unit/test_ollama_client.py
Then implement: app/services/ollama_client.py
Then implement: app/services/extraction.py
Then implement: app/api/routes.py and app/main.py
```

### Parallel Example: User Story 2

```text
Write first: tests/unit/test_prompt_safety.py
Write first: tests/integration/test_safety_cases.py
Write first: tests/unit/test_safety_evaluation.py
Then implement safety changes in app/services/extraction.py and app/api/routes.py
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete setup and shared contract/evaluation foundation.
2. Write US1 tests and verify expected failures.
3. Implement local-only inference, extraction, Pydantic response, independent validation, API, and UI.
4. Validate US1 independently; do not begin with optional comparison.

### Incremental Delivery

1. Add US2 protections and run relevant fixed cases without changing their expected outcomes.
2. Implement US3 only if it does not threaten core requirements; otherwise record the deferral and preserve E-18.
3. Freeze the complete evaluation configuration and rubric before final evaluation; retain initial failures and repair evidence, then rerun the identical E-01–E-20 suite and thresholds.
4. Score every applicable initial and final case on all four rubric dimensions; preserve case-level scores and calculate the final aggregate before report generation.
5. Obtain and preserve human ACCEPT/REJECT after reviewing final evidence.
