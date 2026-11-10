import pytest
from pydantic import ValidationError

from app.schemas.extraction import AnalysisResponse


def test_response_rejects_impossible_date_and_extra_properties():
    payload = {
        "schema_version": "1.0",
        "company_name": {
            "value": "Acme",
            "status": "extracted",
            "evidence": "Acme",
            "message": None,
        },
        **{
            name: {
                "value": "2027-02-30" if name == "opening_date" else None,
                "status": "extracted" if name == "opening_date" else "missing",
                "evidence": "30 February 2027" if name == "opening_date" else None,
                "message": None if name == "opening_date" else "Not stated",
            }
            for name in (
                "opening_date",
                "closing_date",
                "allotment_date",
                "refund_date",
                "listing_date",
            )
        },
        "summary": "Acme IPO schedule.",
        "warnings": [],
        "validation": {"valid": True, "errors": [], "checks": []},
        "injection_detected": False,
    }

    with pytest.raises(ValidationError):
        AnalysisResponse.model_validate(payload)

    payload["opening_date"]["value"] = None
    payload["opening_date"]["status"] = "missing"
    payload["opening_date"]["evidence"] = None
    payload["opening_date"]["message"] = "Not stated"
    payload["unexpected"] = True
    with pytest.raises(ValidationError):
        AnalysisResponse.model_validate(payload)
