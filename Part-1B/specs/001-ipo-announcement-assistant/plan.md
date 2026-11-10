# Implementation Plan: AI-Powered IPO Announcement & Deadline Assistant

**Branch**: `001-ipo-announcement-assistant` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-ipo-announcement-assistant/spec.md`

## Summary

Build a small, single-user local web application for pasted English IPO announcements. A FastAPI
backend will call only a local Ollama service, validate and normalize model results into a strict
versioned Pydantic response, independently enforce date invariants, and serve a simple interface
showing facts, uncertainty, warnings, and validation status. A separate fixed evaluation harness
will exercise the application boundary and preserve schema/invariant checks, field-level scores,
four-dimension semantic rubric scores, failures, repairs, and final human review evidence.

The optional manually entered comparison feature is secondary and may be deferred if it threatens
the extraction, validation, or evaluation gates.

## Technical Context

**Language/Version**: Python 3.11 or newer; Python 3.11 is the project baseline based on Part 1A.

**Primary Dependencies**: FastAPI, Pydantic, Uvicorn, HTTPX for local Ollama communication and
testing, pytest, and a minimal server-rendered HTML/CSS/JavaScript interface.

**Storage**: None for application submissions or records. Evaluation fixtures and evidence are
local files. No database or Part 1A database coupling is required.

**Testing**: pytest; FastAPI TestClient/HTTPX for route and contract tests; deterministic unit tests
for schema/date invariants; fixed Ollama-backed evaluation cases with separately scored semantic
rubric. The independent harness MUST contain the complete, authoritative 20-case set E-01 through
E-20 from the specification and [data-model.md](data-model.md), with one fixed input, expected
output or behavior, requirement links, and case-specific evaluation criteria per case. No case may
be dropped when the optional comparison feature is deferred; E-18 must then evaluate and record
the approved deferral disposition.

**Target Platform**: Locally run desktop environment with Python and Ollama installed; user
accesses the application through a local browser. No cloud deployment.

**Project Type**: Single local web application with a Python backend and static/server-rendered UI.

**Performance Goals**: No model-response latency SLA is specified. Record local end-to-end inference
latency and failures for context; do not make hardware-dependent model latency a pass threshold.
Deterministic validation must complete as part of each request before an output is marked valid.

**Constraints**: Ollama local inference only; no paid/cloud AI, remote fallback, paid hosting,
accounts, trading, or unnecessary persistence. Treat input as untrusted. Do not silently truncate
text. Strict schema, date, and chronology checks remain independent of model output. Semantic and
accuracy thresholds are fixed by the constitution and spec before final evaluation.

**Scale/Scope**: One local user and one announcement per analysis request; bounded request size
must be documented and rejected explicitly when exceeded. Comparison is manual, optional, and
deferrable.

## Constitution Check

| Gate | Plan decision | Status |
|---|---|---|
| Local-first / zero additional cost | Ollama on the local machine; no remote inference fallback or paid hosting | PASS |
| Required technology | Python, FastAPI, and Pydantic; local browser UI | PASS |
| Uncertainty and no invention | Null/status representation, source-grounded summaries, conflict warnings, no silent date inference | PASS |
| Independent validation | Pydantic contract validation plus independent parsing/calendar and chronology checks | PASS |
| Security | Announcement is untrusted data; task/source separation, bounded prompt, output validation, injection cases, no secret logging | PASS |
| Independent evaluation and traceability | Fixed cases map to requirements; independent harness checks invariants and produces preserved evidence | PASS |
| Thresholds and repairs | Predeclared constitution thresholds, unchanged suite after repairs, retained initial/final results | PASS |
| Human accountability | Final reviewer records ACCEPT or REJECT; automated PASS is insufficient | PASS |
| Small local scope | No persistence, accounts, remote integration, or Part 1A DB coupling; comparison may be deferred | PASS |

No constitution violations are identified. Re-check these gates after design and during
implementation; no exception is proposed.

**Post-design re-check**: PASS. The design artifacts preserve local-only inference, independent
validation and evaluation, fixed thresholds, untrusted-input safeguards, human review, and the
constitution's small-scope constraint. No persistence or remote integration is introduced.

## Research Decisions

See [research.md](research.md) for alternatives and rationale. Key decisions:

- Call the Ollama local HTTP service through a small adapter; require a configured local model and
  surface unavailable/timeout errors without fallback.
- Treat model JSON/schema guidance as a formatting aid only. Pydantic and independent invariant
  validation remain authoritative.
- Keep requests and comparison records in memory only; do not persist submitted announcement text.
- Use deterministic expected-value scoring for company/date fields and fixed human-readable rubric
  scoring for summaries and uncertainty, preserving each case's dimension scores.

## Design Artifacts

- [Data model](data-model.md): extraction, field states, validation, evaluation and comparison
  records.
- [OpenAPI contract](contracts/openapi.yaml): versioned analysis request/response boundary and
  explicit failure responses.
- [Quickstart](quickstart.md): local prerequisites and validation procedure; no application
  implementation is included.

## Project Structure

### Documentation (this feature)

```text
specs/001-ipo-announcement-assistant/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
├── checklists/
│   └── requirements.md
└── spec.md
```

### Source Code (repository root)

```text
app/
├── main.py                 # FastAPI app and static/template mounting
├── api/
│   └── routes.py           # HTTP endpoints and request/response mapping
├── schemas/
│   └── extraction.py       # Versioned Pydantic contracts
├── services/
│   ├── ollama_client.py    # Local-only inference adapter
│   ├── extraction.py       # Prompt construction and response parsing
│   └── validation.py       # Date parsing, source support, chronology checks
├── templates/
│   └── index.html          # Single-page local workflow
└── static/
    ├── app.js
    └── styles.css

evaluation/
├── cases.json              # All 20 fixed cases E-01–E-20, inputs, expectations, criteria, FR links
├── harness.py              # Independent runner and metric aggregation
├── rubric.md               # Frozen four-dimension scoring anchors and instructions
└── evidence/
    ├── initial/
    ├── repairs/
    └── final/

tests/
├── unit/
├── contract/
└── integration/
```

**Structure Decision**: Use one Python application package for API, schema, local model adapter,
validation, and static UI; isolate the evaluation harness and its case data from application
implementation. Keep test layers separate. Do not add a separate frontend build system, database,
or Part 1A integration service for this scope.

**Fixed evaluation set**: The specification's E-01 through E-20 cases are authoritative. The
case manifest MUST retain each case's own input, complete expected company/date values and states
or expected operational behavior, applicable requirements, summary/uncertainty scoring
applicability, and explicit pass criteria. The suite, fixtures, and thresholds remain unchanged
between initial and final evaluation; repairs are assessed by rerunning the same 20 cases.

**Evaluation gates**: Before the final run, freeze the model/version and inference configuration,
case manifest, and scoring instructions. Require 100% schema validity, 100% date-invariant
compliance, zero invented dates, at least 90% field-level extraction accuracy, at least 85%
summary and uncertainty quality, and 100% rejection or safe handling of prompt-injection attempts.
Calculate date-invariant compliance per FR-024 as applicable date-field and chronology checks
passed divided by total applicable checks, multiplied by 100; report the numerator, denominator,
and percentage. Use at most one date-field check per date field per case, applicable when the
output is non-null or the source has date candidates. Verified values must exactly match a uniquely
interpretable, source-supported, valid calendar date in ISO form. Invalid, ambiguous, conflicting,
or unsupported candidates pass only when returned null, not verified, and correctly labeled;
non-null unsupported values fail. Omitting a valid, unambiguous source date does not violate date
invariants; field accuracy scores that omission. Verified values must satisfy every applicable
chronology invariant. A chronology check applies once per declared relationship when both source
dates are available and parseable; the relationships are opening <= closing, closing <= allotment,
allotment <= refund, and allotment <= listing, with no ordering between refund and listing. A check
passes when a valid relationship is respected or a source violation is reported and the affected
dates are null and not verified. Missing dates and relationships requiring them are not failures.
Impossible or incorrectly verified dates fail.
The fixed set must yield a nonzero denominator; otherwise the metric is N/A and the gate fails.
Field accuracy is `100 × correct expected company/date fields / total expected company/date
fields`, with numerator and denominator reported. Summary/uncertainty quality uses the four
equally weighted FR-022 dimensions—factual grounding, completeness, concise relevance, and
correct handling of missing/ambiguous/contradictory information—each scored `0`, `0.5`, or `1`;
report `100 × awarded rubric points / available rubric points` and preserve case-level scores.
Retain initial failures, linked repair rationale/evidence, and final results for the same fixed
20-case suite.

## Implementation Sequence Guidance

This plan does not implement the application or create task-level work items. The later task
workflow MUST preserve test-first traceability: create requirement-linked failing tests before
implementing each behavior, implement the simplest compliant behavior, then run and record
validation. Comparison work is lower priority and may be omitted with a recorded deferral if core
gates are at risk.
