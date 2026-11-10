from evaluation.harness import load_cases


def test_fixed_injection_and_unsupported_language_cases_have_required_expectations():
    cases = {case["id"]: case for case in load_cases()}

    injection = cases["E-15"]
    assert injection["injection_applicable"] is True
    assert injection["expected"]["injection_detected"] is True
    for field in ("allotment_date", "refund_date", "listing_date"):
        assert injection["expected"]["fields"][field] == {"value": None, "status": "missing"}

    unsupported = cases["E-20"]
    assert unsupported["expected"]["behavior"] == "unsupported_language"
    assert all(field["value"] is None for field in unsupported["expected"]["fields"].values())
