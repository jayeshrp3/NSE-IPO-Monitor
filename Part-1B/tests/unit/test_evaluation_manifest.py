import json
from pathlib import Path

from evaluation.harness import load_cases


def test_fixed_manifest_has_all_twenty_complete_cases():
    cases = load_cases(Path("evaluation/cases.json"))

    assert [case["id"] for case in cases] == [f"E-{number:02}" for number in range(1, 21)]
    for case in cases:
        assert case["input"] or case["setup"]
        assert case["expected"]
        assert case["criteria"]
        assert case["requirements"]
        if case["expected"].get("fields"):
            assert set(case["expected"]["fields"]) == {
                "company_name",
                "opening_date",
                "closing_date",
                "allotment_date",
                "refund_date",
                "listing_date",
            }
            assert all(
                set(field) == {"value", "status"} for field in case["expected"]["fields"].values()
            )


def test_manifest_is_valid_json_and_has_no_duplicate_ids():
    data = json.loads(Path("evaluation/cases.json").read_text(encoding="utf-8"))

    assert len({case["id"] for case in data["cases"]}) == 20
