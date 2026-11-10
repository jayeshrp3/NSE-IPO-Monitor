from pathlib import Path

import pytest

from evaluation.harness import (
    _select_final_report,
    api_error_is_valid,
    date_invariant_compliance,
    field_accuracy,
    score_quality,
)


def test_field_accuracy_reports_numerator_denominator_and_percent():
    cases = [
        {
            "expected": {"fields": {"company_name": "Acme", "opening_date": None}},
            "result": {
                "company_name": {"value": "Acme", "status": "extracted"},
                "opening_date": {"value": None, "status": "missing"},
            },
            "field_applicable": True,
        }
    ]

    assert field_accuracy(cases) == {"passed": 2, "total": 2, "percentage": 100.0}


def test_quality_requires_individual_four_dimension_scores():
    scores = {
        "E-01": {
            "factual_grounding": 1,
            "completeness": 0.5,
            "concise_relevance": 1,
            "uncertainty_handling": 1,
        }
    }

    assert score_quality(scores) == {
        "awarded": 3.5,
        "available": 4,
        "percentage": 87.5,
        "case_totals": {"E-01": 3.5},
    }


def test_final_report_selection_requires_explicit_id_when_reports_are_ambiguous():
    reports = [
        (Path("first.json"), {"run_id": "first"}),
        (Path("second.json"), {"run_id": "second"}),
    ]

    with pytest.raises(ValueError, match="--report-id"):
        _select_final_report(reports, None)

    assert _select_final_report(reports, "second") == reports[1]


def test_date_invariant_metric_reports_exact_passed_and_applicable_checks():
    cases = [
        {
            "id": "E-01",
            "expected": {
                "behavior": "analysis",
                "fields": {"opening_date": {"value": "2027-02-10", "status": "extracted"}},
            },
            "date_invariant_fields": ["opening_date"],
            "chronology_checks": [],
            "result": {"opening_date": {"value": "2027-02-10", "status": "extracted"}},
        }
    ]

    assert date_invariant_compliance(cases) == {
        "passed": 1,
        "total": 1,
        "percentage": 100.0,
        "checks": [{"case_id": "E-01", "check": "opening_date", "passed": True}],
    }


def test_zero_applicable_date_check_denominator_is_not_a_pass():
    result = date_invariant_compliance([])

    assert result["total"] == 0
    assert result["percentage"] is None


def test_typed_api_errors_are_included_in_independent_schema_validation():
    assert api_error_is_valid(
        {"code": "ollama_unavailable", "message": "Local model is unavailable."}
    )
    assert not api_error_is_valid(
        {"code": "invalid_model_output", "message": "Bad response", "raw_output": "secret"}
    )


def test_date_metric_accepts_correctly_flagged_unresolved_and_chronology_cases():
    cases = [
        {
            "id": "valid",
            "expected": {
                "behavior": "analysis",
                "fields": {"opening_date": {"value": "2027-02-10", "status": "extracted"}},
            },
            "date_invariant_fields": ["opening_date"],
            "chronology_checks": [],
            "result": {"opening_date": {"value": "2027-02-10", "status": "extracted"}},
        },
        {
            "id": "impossible",
            "expected": {
                "behavior": "invalid_source_date",
                "fields": {"opening_date": {"value": None, "status": "invalid"}},
            },
            "date_invariant_fields": ["opening_date"],
            "chronology_checks": [],
            "result": {"opening_date": {"value": None, "status": "invalid"}},
        },
        {
            "id": "ambiguous",
            "expected": {
                "behavior": "analysis",
                "fields": {"opening_date": {"value": None, "status": "ambiguous"}},
            },
            "date_invariant_fields": ["opening_date"],
            "chronology_checks": [],
            "result": {"opening_date": {"value": None, "status": "ambiguous"}},
        },
        {
            "id": "conflicting",
            "expected": {
                "behavior": "analysis",
                "fields": {"opening_date": {"value": None, "status": "contradictory"}},
            },
            "date_invariant_fields": ["opening_date"],
            "chronology_checks": [],
            "result": {"opening_date": {"value": None, "status": "contradictory"}},
        },
        {
            "id": "unsupported",
            "expected": {
                "behavior": "unsupported_language",
                "fields": {"opening_date": {"value": None, "status": "uncertain"}},
            },
            "date_invariant_fields": ["opening_date"],
            "chronology_checks": [],
            "result": {"opening_date": {"value": None, "status": "uncertain"}},
        },
        {
            "id": "chronology",
            "expected": {
                "behavior": "chronology_failure",
                "fields": {
                    "opening_date": {"value": None, "status": "contradictory"},
                    "closing_date": {"value": None, "status": "contradictory"},
                },
            },
            "date_invariant_fields": ["opening_date", "closing_date"],
            "chronology_checks": ["opening_date:closing_date"],
            "result": {
                "opening_date": {"value": None, "status": "contradictory"},
                "closing_date": {"value": None, "status": "contradictory"},
                "validation": {"valid": False},
            },
        },
        {
            "id": "missing",
            "expected": {"behavior": "analysis", "fields": {}},
            "date_invariant_fields": [],
            "chronology_checks": [],
            "result": {},
        },
    ]

    result = date_invariant_compliance(cases)

    assert result["passed"] == 8
    assert result["total"] == 8
    assert result["percentage"] == 100.0
