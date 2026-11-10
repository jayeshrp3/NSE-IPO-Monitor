# AI-Powered IPO Announcement & Deadline Assistant

Part 1B is a local-only, single-user application for extracting IPO dates and company details
from English announcements. It uses Python, FastAPI, Pydantic, and a locally running Ollama
model. It does not use cloud AI, paid APIs, accounts, databases, or remote inference fallback.

## Local setup

Requirements: Python 3.11+ and Ollama with a model already downloaded locally.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
ollama pull qwen2.5:3b
$env:OLLAMA_MODEL = "qwen2.5:3b"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. Configure only a loopback Ollama endpoint using
`OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`), `OLLAMA_MODEL`, and
`OLLAMA_TIMEOUT_SECONDS`. The application rejects non-loopback inference endpoints. Requests are
limited to 50,000 Unicode characters; oversized content is rejected without truncation. Submissions
are not persisted.

Only English is supported. Dates are normalized to ISO `YYYY-MM-DD` only when supported by the
source and independently validated. Missing, ambiguous, conflicting, unsupported, or invalid
dates remain unverified and carry a status or warning. The browser renders model/source text as
literal text.

## Tests and independent evaluation

Run automated tests and lint:

```powershell
python -m pytest
python -m ruff check app evaluation tests
```

The independent fixed suite contains E-01 through E-20 in `evaluation/cases.json`. Once Ollama is
running and the configured model is locally available, record the initial evaluation with:

```powershell
python -m evaluation.harness run --phase initial
```

Before any final evaluation, freeze the selected model/version, Ollama settings, all 20 case IDs,
the FR-024 date-invariant methodology, thresholds, and rubric:

```powershell
python -m evaluation.harness freeze
```

Review the initial case outputs and preserve a 0/0.5/1 score for each applicable case on all four
equally weighted quality dimensions in `evaluation/evidence/initial/rubric-scores.json`. Record
these scores using `evaluation/rubric-scores-template.json` as a starting point, replacing every
`null` with a human-assigned score. Record repairs without changing the suite or thresholds. After repairs, run the final suite with
`python -m evaluation.harness run --phase final`; the harness prints the report run ID. Score each
applicable final case in `evaluation/evidence/final/rubric-scores.json`, then apply those scores to
that specific report with
`python -m evaluation.harness score --report-id <run-id>`. The explicit ID is required when more
than one unscored final report is preserved. Record a human ACCEPT or REJECT decision. Final
acceptance requires all constitution thresholds; an unscored case, zero FR-024 denominator,
unavailable Ollama/model, or threshold failure prevents ACCEPT.

Thresholds are: 100% response schema validity; 100% date-invariant compliance with a nonzero
denominator; zero invented dates; at least 90% field-level accuracy; at least 85% summary and
uncertainty quality; and 100% safe handling of prompt injection. FR-024 results include passed
checks, applicable checks, and percentage. See `evaluation/rubric.md` and the feature specification
for scoring rules and case expectations. `evaluation/traceability.json` links each functional
requirement to implementation files, tests, and fixed evaluation cases. Use
`evaluation/human-review-template.md` to record the required final human ACCEPT or REJECT decision;
the harness cannot accept on a human's behalf.

The optional manual comparison with Part 1A is deferred for this implementation; case E-18 remains
in the fixed evaluation set and records that disposition.

