# AI-Powered IPO Announcement & Deadline Assistant (Part 1B) Constitution

## Core Principles

### I. Local-First AI
The application MUST use a locally running Ollama model for AI inference. It MUST NOT call paid APIs, use subscriptions, depend on cloud AI services, or require paid hosting. The application and evaluation harness MUST be runnable locally at zero additional cost. The selected model, version, and relevant inference settings MUST be recorded with evaluation evidence.

### II. Structured and Reliable Extraction
The application MUST be implemented in Python with FastAPI and Pydantic. IPO extraction results MUST conform to a strict, versioned Pydantic schema. The application MUST independently validate required fields, date formats, and date relationships after inference; model-produced structured output MUST NOT bypass these checks. API, extraction, validation, and evaluation responsibilities MUST remain separated sufficiently to test independently.

### III. Uncertainty Transparency
The application MUST accept IPO announcement text and extract the company name and, where available, opening, closing, allotment, refund, and listing dates. It MUST generate a concise summary grounded in that text. Missing, ambiguous, contradictory, or uncertain details MUST be identified in the response. The application MUST NOT invent missing dates, silently resolve contradictions, or present unsupported inference as fact. A missing value MUST remain missing in the output.

### IV. Independent Evaluation
The evaluation harness MUST be independent of application implementation and MUST assess schema conformance, deterministic invariants and property-based checks, and semantic or quality criteria. It MUST contain at least 15 distinct, meaningful cases, covering valid announcements and relevant missing, ambiguous, contradictory, malformed, and adversarial content. Evaluation cases MUST remain fixed for final evaluation and MUST not be weakened to obtain a passing result.

Before the final evaluation is run, the project MUST document measurable metrics and pass thresholds. The final gate MUST require 100% schema validity, 100% date-invariant compliance, zero invented dates, at least 90% field-level extraction accuracy, at least 85% summary and uncertainty quality under a documented rubric, and 100% rejection or safe handling of prompt-injection attempts. Date-invariant compliance MUST be calculated as `(applicable date-invariant checks passed / total applicable date-invariant checks) × 100`, with numerator, denominator, and percentage reported. Create at most one date-field check per date field per case; it applies when the output contains a non-null date or the source contains one or more date candidates for that field. A verified value passes only when it exactly matches the uniquely interpretable, source-supported, valid calendar date in normalized ISO form and satisfies every applicable chronology invariant. A field with an impossible, ambiguous, conflicting, or unsupported source candidate passes only when it is returned null, not marked verified, and its state is correctly reported. Omitting a valid, unambiguous source date does not violate date invariants because no date is verified; field-level extraction accuracy scores that omission. A non-null value with no source support fails. A chronology check applies once per declared relationship when both source dates are explicitly available and individually parseable; the declared relationships are opening <= closing, closing <= allotment, allotment <= refund, and allotment <= listing, with no ordering between refund and listing. It passes when verified dates respect a valid relationship, or when a source chronology violation is detected/reported and the affected dates are returned null and not verified. Missing dates do not fail solely because they are absent, and relationships requiring a missing date are not applicable. Any impossible or incorrectly verified date fails its applicable check. The denominator MUST be nonzero for the fixed evaluation set; otherwise the metric is N/A and the evaluation gate fails. The semantic rubric and case-level scoring MUST be recorded before final evaluation.

### V. Test-Driven Development and Traceability
Evaluation cases and tests MUST be derived from approved specification requirements before the corresponding implementation is considered complete. Each requirement MUST map to one or more implementation components and evaluation cases, and each evaluation case MUST identify the requirement it verifies. Development MUST follow a test-first cycle: define or update the requirement and its failing test before implementing behavior, then run the test and preserve its result.

Initial failures and their evidence MUST be retained. Repairs MUST be documented and linked to the failure they address. The same evaluation suite and predeclared thresholds MUST be rerun after repairs, and final results MUST be retained alongside initial failures and repair evidence. No failure evidence may be erased or misrepresented as a pass.

### VI. Security and Untrusted Input
Announcement text MUST be treated as untrusted data, not as instructions to the model, application, or evaluation harness. The system MUST include prompt-injection safeguards, delimit or otherwise isolate source content from task instructions, and constrain model output to the extraction and summarization task. It MUST validate model output before use and safely report invalid results without fabricating a successful response. Logs and evaluation artifacts MUST not expose secrets or unnecessary sensitive data.

## Additional Constraints

The required stack is Python, FastAPI, Pydantic, and locally running Ollama. External inference services and paid infrastructure are prohibited. The project MUST remain small and locally runnable; persistence, user accounts, deployment, and other features not required by the approved specification MUST NOT be added without an explicit amendment or approved scope change. API responses MUST identify their schema version. IPO date fields MUST use a documented unambiguous date representation, and validation MUST enforce applicable chronological relationships without assuming dates absent from the source.

The minimum evaluation matrix MUST include at least these 15 distinct case types, each linked to its requirement and expected outcome:

1. Complete announcement with all six requested fields present.
2. Announcement with opening and closing dates only.
3. Missing company name.
4. Missing opening date.
5. Missing closing date.
6. Missing allotment date.
7. Missing refund date.
8. Missing listing date.
9. Ambiguous numeric date format.
10. Conflicting opening dates in one announcement.
11. Conflicting closing dates in one announcement.
12. Closing date earlier than opening date.
13. Malformed or impossible calendar date.
14. Unrelated or non-IPO text.
15. Prompt injection instructing the model to disregard its task or fabricate dates.

Cases MUST include representative source text and explicit expected extraction, uncertainty, schema, and safety outcomes. Additional cases MUST be added when requirements introduce behavior not covered by this minimum set.

## Development Workflow

The approved specification MUST define requirements and acceptance criteria before implementation. A traceability record MUST connect each requirement to implementation and evaluation cases. Evaluation metrics, scoring rubric, and thresholds MUST be committed or otherwise recorded before the final evaluation begins. Initial evaluation output, failure evidence, repair rationale, repair evidence, and final evaluation output MUST be preserved as distinct, auditable artifacts. Final evaluation MUST run locally against the declared Ollama model and configuration, and results MUST report any nondeterminism or infrastructure limitation rather than masking it.

Automated gates are necessary but not sufficient for acceptance. A human reviewer MUST inspect the requirements, implementation, evaluation cases, all preserved evidence, threshold results, and known limitations, then explicitly record **ACCEPT** or **REJECT**. A failed automated gate MUST NOT be accepted without a documented, reviewed exception; the zero-invented-dates and schema-validity requirements cannot be waived.

## Governance

This constitution governs Part 1B and supersedes conflicting informal project practices. All specifications, plans, implementation changes, and evaluation decisions MUST comply with it. Amendments MUST state their rationale, affected principles and requirements, compatibility impact, and any changes needed to implementation, traceability, evaluation cases, or thresholds. Amendments require human review before adoption.

Constitution versions MUST follow semantic versioning. A MAJOR increment is required for incompatible changes or removal of a governing requirement; a MINOR increment is required for a new or materially expanded principle or section; a PATCH increment is required for clarifications that do not change requirements. Reviews MUST verify compliance and preserve an auditable record of the final human ACCEPT or REJECT decision.

**Version**: 1.0.0 | **Ratified**: 2026-11-10 | **Last Amended**: 2026-11-10
