# Validation Harness Log — IPO Deadline Tracker Part 1A

This log records executed validation commands, actual outcomes, repair attempts,
preserved evidence, and the final human review decision.

## Current status

- Application implementation: complete.
- Final validation: Pytest 26 passed, Ruff passed, Bandit reported no findings
  after the typed API-response schema change.
- Runtime: Windows, Python 3.14.0; Pytest 9.2.0, Ruff 0.17.4, Bandit 1.9.4,
  Playwright Chromium 143.
- Harness database: a fresh temporary `IPO_DATABASE_PATH` per test; default
  alert threshold 3, with separate 0, 5, malformed, and negative setting cases.
- Credential-pattern scan of `app/`, `frontend/`, and `pyproject.toml`: no
  matches for password, secret, API key, credential, or token assignments.
- Human decision: PENDING; automated checks do not constitute acceptance.

## Validation and repair history

The standard gates are:

1. `python -m pytest validation/harness -q`
2. `python -m ruff check .`
3. `python -m bandit -r app`

The initial set ran without output redirection. Subsequent PowerShell runs used
`2>&1 | Tee-Object -FilePath <evidence-file>; exit $LASTEXITCODE` to preserve
the actual output; the underlying three commands were unchanged.

| Date/time (UTC) | Snapshot | Pytest | Ruff | Bandit | Failure / repair evidence |
|---|---|---|---|---|---|
| 2026-11-10 10:34 (parallel run; Bandit start 10:34:24) | `initial/initial-source.zip` | Exit 1; 14 passed, 2 failed, 32.73s | Exit 1; 19 findings | Exit 0; no findings, 732 lines | Duplicate wording and static URL selector test failures; initial Ruff output in `initial/ruff-first-run.txt`. |
| 2026-11-10 10:36 (Bandit start 10:36:01) | `repaired/repaired-source-1.zip` | Exit 0; 16 passed, 32.17s | Exit 0 | Exit 0; no findings, 756 lines | Duplicate wording, URL assertion, imports, FastAPI dependency style, and line wrapping repaired. |
| 2026-11-10 10:41 (Bandit start 10:41:30) | `repaired/repaired-source-2.zip` | Exit 0; 21 passed, 51.56s | Exit 1; 2 findings | Exit 0; no findings, 811 lines | Expanded corruption, status, threshold, and integrity checks; Ruff identified import modernization issues. |
| 2026-11-10 10:43 (Bandit start 10:43:37) | `repaired/repaired-source-3.zip` | Exit 0; 21 passed, 55.42s | Exit 0 | Exit 0; no findings, 811 lines | Applied Ruff's safe import fixes and reran all gates. |
| 2026-11-10 10:46 (Bandit start 10:46:31) | `repaired/repaired-source-4.zip` | Exit 1; 23 passed, 2 browser-test failures, 72.11s | Exit 0 | Exit 0; no findings, 811 lines | One URL wait matched the edit page; one text locator was ambiguous. |
| 2026-11-10 10:48 (Bandit start 10:48:18) | `repaired/repaired-source-5.zip` | Exit 1; 24 passed, 1 browser-test failure, 52.09s | Exit 0 | Exit 0; no findings, 811 lines | Browser navigation invalidated a response-body read; test changed to await the detail URL. |
| 2026-11-10 10:49 (Bandit start 10:49:51) | `repaired/repaired-source-6.zip` | Exit 0; 25 passed, 50.55s | Exit 1; 1 import-order finding | Exit 0; no findings, 811 lines | Corrected the browser test import order. |
| 2026-11-10 10:51 (Bandit start 10:51:39) | `repaired/repaired-source-7.zip` | Exit 0; 25 passed, 46.35s | Exit 0 | Exit 0; no findings, 811 lines | All gates passed. |
| 2026-11-10 10:53 (Bandit start 10:53:24) | `repaired/repaired-source-8.zip` | Exit 0; 26 passed, 43.56s | Exit 0 | Exit 0; no findings, 811 lines | Added configured-positive-threshold and no-result filter assertions; all gates passed. |
| 2026-11-10 10:55 (Bandit start 10:55:14) | `repaired/repaired-source-9.zip` | Exit 0; 26 passed, 44.00s | Exit 0 | Exit 0; no findings, 811 lines | Final exact validation-error and tie-order assertions; all gates passed. |
| 2026-11-10 10:57 (Bandit start 10:57:31) | `repaired/repaired-source-10.zip` | Exit 0; 26 passed, 46.57s | Exit 0 | Exit 0; no findings, 829 lines | Added typed response schemas and OpenAPI response validation; all gates passed. |

Rerun output files are preserved as `pytest-rerun-N.txt`,
`ruff-rerun-N.txt`, and `bandit-rerun-N.txt` in
`validation/evidence/repaired/`. Every repair was followed by the same
Pytest/Ruff/Bandit gate set. Earlier failures remain preserved and have not
been replaced by passing results.

## Repair evidence

- Initial implementation and baseline evidence:
  `validation/evidence/initial/initial-source.zip` and
  `validation/evidence/initial/ruff-first-run.txt`.
- Repaired source snapshots and corresponding rerun evidence:
  `validation/evidence/repaired/`.
- No credentials, secrets, or unrelated user data are included.

## Human review

- Decision: ACCEPT
- Reviewer: PATIL JAYESH RAVINDRA SARLA
- Date: 2026-11-10
- Evidence reviewed:
  - Initial and repaired source snapshots
  - Pytest validation results
  - Ruff validation results
  - Bandit validation results
  - Repair history and final validation results
- Known limitations and residual risks: Public holidays are not excluded
  from the weekday-based listing-date calculation; IPO information is
  user-entered and is not synchronized with NSE.
- Rationale: The implementation and final validation evidence were
  reviewed. All final automated validation gates passed, and the known
  limitations are documented and understood.
