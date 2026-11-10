# Implementation Repair Evidence

The test-first baseline was run before implementation and failed collection because the planned
application and evaluation modules did not yet exist. That red baseline was expected; it is retained
in the session test output. The implementation then added the missing modules before behavior tests
were considered complete.

| Finding | Repair |
|---|---|
| Over-limit Pydantic request errors were using FastAPI's default nested error envelope. | Added typed request and HTTP error handlers; the 50,001-character request now returns `input_too_large` before inference. |
| Natural-language date parsing missed dates after field terms because a generic month-name alternative consumed preceding words. | Restricted parsing to recognized month names and added fixed-case candidate extraction by date-field context. |
| The first validator trusted a model-selected date when the source contained conflicting candidates. | Added independent field-specific source candidate checks; ambiguity and conflicts now force null, unverified values. |
| Chronology checks depended on model-selected values and could miss source violations when the model returned null. | Recomputed chronology from independently extracted source candidates and invalidated affected schedule dates. |
| Impossible dates could fail Pydantic parsing before a safe unresolved analysis was produced. | Kept model candidate parsing separate from API response validation; impossible source dates now become null/`invalid` with a failed independent validation. |
| The initial asynchronous client test depended on an undeclared pytest plugin. | Rewrote the test using `asyncio.run`; no test-only plugin was added. |
| Prompt content shared one flat text prompt and could contain closing delimiter text. | Switched to separate Ollama system/user messages and JSON-encoded the announcement as untrusted data. |
| Evaluation initially counted absent results as zero invented dates and treated E-18 deferral alone as an operation pass. | Corrected unscorable-date accounting and require E-18 extraction to succeed; added dataset hash and case applicability to evaluation records. |
| The first manifest flag excluded E-20 from field scoring despite the spec's shared evaluation rule. | Corrected only E-20 metric applicability; retained its exact input, unsupported-language behavior, and unverified-value requirement. |
| The independent schema metric counted only analysis responses, omitted E-20's FR-024 date-field checks, and did not verify the typed API-error schema. | Updated scoring to validate each of the 20 success/error response contracts, include E-20's two source-date checks, and preserve the original fixed inputs and requirements. |
| Natural-language date evidence needed additional calendar forms, while year inference could overstate certainty when announcements mentioned multiple years. | Added ordinal-day parsing, rejected implicit-year candidates when the source has multiple distinct years, and added a regression test that prevents an unsupported year from being verified. |
| Qwen returned null/omitted field objects and marked injection-requested dates as `inferred`; strict parsing rejected the entire otherwise-valid response before independent verification. | Normalize absent/null model fields to unresolved candidates, discard model-inferred values, recover only uniquely source-supported dates and IPO-adjacent company names, and preserve strict validation of the public response. Added focused regression tests. |
| Multiple preserved final reports prevented unambiguous rubric finalization after a new rerun. | Added explicit final report ID selection to the score command and print the new report run ID after each evaluation. |

No acceptance threshold, case input, or required behavior was removed. The first 20-case evaluation
is preserved as the initial baseline; a corrected initial run is retained separately after these
harness repairs. Ollama was unavailable locally, so model-dependent cases timed out and no final
evaluation was run.

After the date-parsing repair, `python -m ruff check app evaluation tests` passed and
`python -m pytest -q` passed all 36 tests. The later model-output recovery changes were verified
with Ruff and all 44 tests. The 20-case initial evaluation is preserved in
`../initial/99abed98-1457-4908-8d4b-94f049f102ac.json`; Ollama was unavailable during that run, so
it is failure evidence rather than a final acceptance evaluation.

Replay verification after repair: the captured Qwen response shapes for E-02, E-07, E-11, E-12, E-13, E-14, E-15, and E-18 produced the expected extracted/missing/contradictory/invalid statuses; the subset scored 42/42 field checks and 34/34 date-invariant checks (100% each). This is a focused replay, not a replacement for rerunning the complete final E-01–E-20 evaluation. All 44 automated tests and Ruff checks pass.
