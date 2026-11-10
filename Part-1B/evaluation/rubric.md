# Summary and Uncertainty Quality Rubric

Score each applicable case independently. Preserve all four case-level scores and the case total.
Each dimension is equally weighted and may be scored only `0`, `0.5`, or `1`.

| Dimension | 1 | 0.5 | 0 |
|---|---|---|---|
| Factual grounding | Every material claim is supported by the announcement. | Mostly grounded, with one minor unsupported or imprecise claim. | A material claim is unsupported. |
| Completeness | Covers all material announced facts and relevant missing/conflicting information. | Omits one noncritical item. | Omits a material fact or uncertainty. |
| Concise relevance | Concise and limited to relevant IPO information. | Mostly relevant but noticeably verbose or slightly irrelevant. | Predominantly irrelevant or unusable. |
| Uncertainty handling | Missing, ambiguous, and contradictory information is correctly identified and not verified. | Mostly correct with one noncritical status/warning omission. | Material uncertainty is misrepresented or concealed. |

Aggregate quality is `100 × awarded rubric points / available rubric points`. Operational cases
with no analysis output are not scored. A missing case score is not a zero and blocks the final
quality gate until a human reviewer records it.

Scores must be recorded before generating the aggregate report. Never infer semantic scores from
schema or model confidence.
