# Quickstart Validation Guide

This guide describes how to run the IPO Deadline Tracker and its independent
validation gates.

## Prerequisites

- Python 3.11+
- Virtual environment with dependencies installed
- SQLite available in the local runtime
- Pytest installed for validation runs
- Ruff and Bandit installed for linting and security checks
- Playwright Chromium installed for browser-level UI confirmation checks
- The application can be started against an isolated SQLite database and
  configured with `IPO_ALERT_THRESHOLD`

## Validation Steps

### 1. Install dependencies

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m playwright install chromium
```

### 2. Start the application

Start the app against an isolated test database and set the threshold (or leave
it unset to verify the default). In PowerShell:

```powershell
$env:IPO_DATABASE_PATH = ".\validation\ipo-harness.sqlite3"
$env:IPO_ALERT_THRESHOLD = "3"
python -m uvicorn app.main:app
```

Keep the server running in one terminal.
The harness MUST use its own isolated database path rather than a developer's
or production database.

### 3. Run the independent acceptance and contract harness

```bash
python -m pytest validation/harness -q
```

The harness starts the application as a separate Uvicorn process using a
temporary SQLite database for each test. It exercises only public HTTP and
browser-visible interfaces and MUST not import application implementation
modules. It covers
API contracts, CRUD, validation, duplicate rejection, date boundaries and
listing-date rules, thresholds, optional-date update semantics, deletion
confirmation, corrupted-data handling, search, filtering, sorting, and database
integrity. Expected outcomes are defined by the acceptance criteria; record
actual results in `harness-log.md`, not assumed results.

### 4. Run Ruff

```bash
python -m ruff check .
```

Record the actual command, output, and result in `harness-log.md`.

### 5. Run Bandit

```bash
python -m bandit -r app
```

Record the actual command, output, and result in `harness-log.md`.

### 6. Preserve evidence and repair

```bash
python -m pytest validation/harness -q
python -m ruff check .
python -m bandit -r app
```

When a repair is needed, preserve the initial implementation and its validation
evidence under `validation/evidence/initial/`, preserve the repaired
implementation and evidence under `validation/evidence/repaired/`, and rerun
the exact same three checks. Log each command, result, failure, repair, and
rerun outcome in `harness-log.md`. Do not replace failed results with later
passing results or report a check as passing unless it was run.

## Expected Outcomes

The implementation is considered ready for human review only when:

- all required independent harness checks pass with recorded evidence,
- boundary and expired-date logic is proven,
- duplicate detection rules are enforced,
- alert threshold behavior is validated,
- Ruff and Bandit results are recorded and reviewed,
- and the feature’s behavior matches the approved specification and constitution.

A human reviewer MUST inspect the implementation, evidence, known limitations,
and residual risks, then record an explicit ACCEPT or REJECT decision and
rationale in `harness-log.md`. No human decision is implied by automated test
results.
