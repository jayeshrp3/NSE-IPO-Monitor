# Local Validation Quickstart

This is a validation guide for the planned application. It contains no implementation code.

## Prerequisites

- Python 3.11 or newer.
- Ollama installed and running locally.
- A locally downloaded model configured for the application.
- Project dependencies installed from the eventual project manifest.

No paid API, cloud model, remote inference fallback, or paid hosting is used.

## Start the local service

1. Start Ollama and verify the configured model is available locally.
2. Start the FastAPI application using the project's documented development command.
3. Open the local interface at `http://127.0.0.1:8000`.
4. Paste an English IPO announcement and submit it.
5. Confirm the interface shows company/date fields, summary, field-level statuses, warnings,
   schema version, and independent validation result.

From the Part-1B project directory, create and activate a virtual environment, install
`python -m pip install -e ".[dev]"`, then start the application with
`python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`. On PowerShell, configure the local
model before startup with `$env:OLLAMA_MODEL = "llama3.2:3b"` (or a model already installed
locally). The default Ollama endpoint is `http://127.0.0.1:11434`; only loopback endpoints are
accepted.

## Focused acceptance checks

1. Complete announcement: all explicitly supported fields normalize correctly and pass schema and
   invariant checks.
2. Missing dates: fields remain null/missing and no date is inferred.
3. Ambiguous/conflicting/impossible dates: affected fields remain unverified and carry warnings.
4. Prompt injection: embedded instructions do not override the extraction task or fabricate facts.
5. Non-English text: unsupported-language warning or safe failure; no verified extraction.
6. Invalid model response: rejected or reported invalid, never displayed as validated.
7. Local Ollama unavailable: explicit local dependency error and no remote fallback.
8. Evaluation: run the unchanged fixed case set, retain initial failures, repair evidence, final
   per-case results, metric numerators/denominators, rubric scores, configuration, and human
   ACCEPT/REJECT decision.

Run the local automated suite with `python -m pytest` and lint with
`python -m ruff check app evaluation tests`. The fixed evaluation harness is run with
`python -m evaluation.harness run --phase initial`; record/freeze the model/version, all 20 cases,
settings, thresholds, and scoring rules with `python -m evaluation.harness freeze` before final
evaluation, then use `--phase final`.

## Final evaluation gates

- 100% response schema validity.
- 100% date-invariant compliance using the FR-024 applicable-check formula; report passed/total checks and percentage. Correctly detecting and reporting invalid source dates or chronology violations counts as a passed check, while impossible or incorrectly verified dates fail.
- Zero invented dates.
- At least 90% field-level extraction accuracy, reported as numerator, denominator, percentage.
- At least 85% summary/uncertainty quality using the four fixed equally weighted rubric dimensions.
- 100% rejection or safe handling of prompt-injection attempts.

Record model and Ollama versions/settings before the final run. Do not change cases, scoring rules,
or thresholds after observing results.
