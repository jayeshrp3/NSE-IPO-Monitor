# Research: AI-Powered IPO Announcement & Deadline Assistant

**Date**: 2026-11-10  
**Scope**: Resolve design choices required by the approved specification and Part 1B constitution.

## Decision: Local Ollama integration

**Decision**: The application calls the locally configured Ollama HTTP service through one
replaceable client adapter. The base URL and model identifier are configuration, defaulting to a
loopback endpoint; remote URLs are rejected or disallowed by configuration. If Ollama or the model
is unavailable, return an explicit failure and never fall back to a hosted model.

**Rationale**: This keeps inference local, avoids binding application logic to a specific model,
and makes the failure mode testable. The model identifier, Ollama version, and relevant inference
settings are captured with each evaluation run.

**Alternatives considered**:

- A paid or hosted inference API: prohibited by the constitution.
- Silent remote fallback: prohibited and unsafe because the user requires local-only processing.
- Calling Ollama throughout route logic: rejected in favor of a narrow adapter that can be stubbed
  in tests.

## Decision: Model output is a proposal, not trusted structured data

**Decision**: Inference instructions request one JSON object conforming to the response shape.
Application code parses and validates it using Pydantic, then performs independent date syntax,
calendar, source support, and chronology checks. A model-provided validation claim is ignored.

**Rationale**: JSON-mode or schema-guided generation can improve formatting but does not replace
validation. The model and Ollama version may differ; correctness cannot depend on their compliance.

**Alternatives considered**:

- Treating valid JSON as valid extraction: rejected because structurally valid output may contain
  impossible, contradictory, invented, or unsupported values.
- Letting the model decide date invariants: rejected because checks must be independent.

## Decision: Evidence and uncertainty representation

**Decision**: Each company/date field has a nullable normalized value, a state (such as
`extracted`, `missing`, `ambiguous`, `contradictory`, or `invalid`), and concise source evidence
or a warning as appropriate. A value with unresolved ambiguity or conflict is not reported as a
verified date.

**Rationale**: Field-level states let both API consumers and the UI distinguish absence from
invalidity and conflict without inventing a substitute.

**Alternatives considered**:

- A single global warning string: rejected because it cannot reliably attribute uncertainty to
  individual fields.
- Best-guess normalization of ambiguous numeric dates: rejected by the no-invention requirement.

## Decision: Local UI and privacy scope

**Decision**: Serve a small browser interface from the local FastAPI application. Keep analysis
request data and manual comparison data in memory for the request/session only; do not add
persistent storage or automatic external retrieval.

**Rationale**: This meets the pasted-text workflow while keeping setup and privacy surface small.

**Alternatives considered**:

- A separate frontend build and remote backend: unnecessary for a single-user local assignment.
- Database persistence: not required by the spec and expands data handling scope.
- Automatic Part 1A database integration: not required; manual comparison is secondary and may be
  deferred.

## Decision: Independent evaluation methodology

**Decision**: Store a fixed set of requirement-linked test cases and expected field states outside
the application package. The harness independently validates schema and invariants and computes
field accuracy as `100 × correct expected company/date fields / total expected company/date
fields`. For applicable cases, assess summaries and uncertainty with the four fixed equally
weighted dimensions, each scored 0, 0.5, or 1; compute quality as `100 × awarded points / available
points` and preserve each case's scores.

**Rationale**: Fixed expectations and formulae make regressions measurable. Human rubric scoring
is transparent and avoids relying on the same model to judge its own output.

**Alternatives considered**:

- An LLM-only judge: rejected because model self-evaluation can be nondeterministic and may share
  the extraction model's failure modes.
- A score without case-level records: rejected because failures must be auditable and repairable.
- Changing cases after a failure: prohibited; the same cases and thresholds must be rerun.

## Decision: Performance and size assumptions

**Decision**: Keep scope to one local user and one announcement per request. No response-time SLA is
specified; record inference latency but do not use hardware-dependent latency as a pass gate.
Reject oversized input with an explicit message rather than silently truncating it.

**Rationale**: Local model hardware varies and no latency target was requested. Explicit limits
prevent uncontrolled inputs without changing announcement meaning.

**Alternatives considered**:

- A fixed latency pass threshold: rejected because hardware/model configuration is unspecified.
- Silent truncation: rejected because omitted text could contain or change relevant dates.

## Decision: English-only first version

**Decision**: Support English announcement text only. Clearly warn or safely fail on other
languages and do not mark any resulting extraction as verified.

**Rationale**: This is explicitly confirmed in the clarification record and makes evaluation scope
fixed.

## Resolved constraints

- Stack: Python 3.11+, FastAPI, Pydantic, Ollama local inference; Python 3.11 aligns with the
  adjacent Part 1A project's declared minimum.
- Storage: no application persistence; local evaluation inputs and evidence are files.
- Comparison: manual values only if implemented; optional and deferrable without removing its
  traceability case.
- Acceptance: all constitutional thresholds remain unchanged and final approval is human
  ACCEPT/REJECT.
