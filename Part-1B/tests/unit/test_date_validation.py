from app.services.validation import validate_dates


def test_impossible_date_is_unverified_and_invalid():
    fields = {
        "opening_date": {
            "value": "2027-02-30",
            "status": "extracted",
            "evidence": "opens 30 February 2027",
            "message": None,
        }
    }

    result = validate_dates(fields, "IPO opens 30 February 2027.")

    assert result["fields"]["opening_date"]["value"] is None
    assert result["fields"]["opening_date"]["status"] == "invalid"
    assert result["validation"]["valid"] is False


def test_missing_date_is_not_a_validation_error():
    fields = {
        name: {
            "value": None,
            "status": "missing",
            "evidence": None,
            "message": "Not stated",
        }
        for name in (
            "opening_date",
            "closing_date",
            "allotment_date",
            "refund_date",
            "listing_date",
        )
    }

    result = validate_dates(fields, "No dates are stated.")

    assert result["validation"]["valid"] is True
    assert all(field["value"] is None for field in result["fields"].values())


def test_complete_supported_ipo_schedule_passes_all_date_invariants():
    source = (
        "Northstar Solar Ltd IPO opens 10 February 2027 and closes 12 February 2027. "
        "Allotment is expected on 15 February, refunds on 17 February, "
        "and listing on 18 February 2027."
    )

    fields = {
        "opening_date": ("2027-02-10", "opens 10 February 2027"),
        "closing_date": ("2027-02-12", "closes 12 February 2027"),
        "allotment_date": (
            "2027-02-15",
            "Allotment is expected on 15 February",
        ),
        "refund_date": ("2027-02-17", "refunds on 17 February"),
        "listing_date": ("2027-02-18", "listing on 18 February 2027"),
    }

    result = validate_dates(
        {
            name: {
                "value": value,
                "status": "extracted",
                "evidence": evidence,
                "message": None,
            }
            for name, (value, evidence) in fields.items()
        },
        source,
    )

    assert result["validation"]["valid"] is True
    assert all(result["fields"][name]["value"] == value for name, (value, _) in fields.items())


def test_chronology_violation_unverifies_affected_dates():
    fields = {
        "opening_date": {
            "value": "2027-02-12",
            "status": "extracted",
            "evidence": "opens 12 February 2027",
            "message": None,
        },
        "closing_date": {
            "value": "2027-02-10",
            "status": "extracted",
            "evidence": "closes 10 February 2027",
            "message": None,
        },
    }

    result = validate_dates(
        fields,
        "IPO opens 12 February 2027 and closes 10 February 2027.",
    )

    assert result["validation"]["valid"] is False
    assert result["fields"]["opening_date"]["status"] == "contradictory"
    assert result["fields"]["closing_date"]["status"] == "contradictory"
    assert result["fields"]["opening_date"]["value"] is None
    assert result["fields"]["closing_date"]["value"] is None


def test_source_conflict_and_ambiguous_numeric_date_override_model_selection():
    conflict_source = (
        "Northstar Solar Ltd IPO opens 10 February 2027. "
        "A correction says opening date is 11 February 2027."
    )

    conflict = validate_dates(
        {
            "opening_date": {
                "value": "2027-02-10",
                "status": "extracted",
                "evidence": "opens 10 February 2027",
                "message": None,
            }
        },
        conflict_source,
    )

    assert conflict["fields"]["opening_date"]["value"] is None
    assert conflict["fields"]["opening_date"]["status"] == "contradictory"

    ambiguous = validate_dates(
        {
            "opening_date": {
                "value": "2027-04-03",
                "status": "extracted",
                "evidence": "opens 03/04/2027",
                "message": None,
            }
        },
        "Northstar Solar Ltd IPO opens 03/04/2027 and closes 6 April 2027.",
    )

    assert ambiguous["fields"]["opening_date"]["value"] is None
    assert ambiguous["fields"]["opening_date"]["status"] == "ambiguous"


def test_year_is_not_inferred_when_announcement_contains_multiple_years():
    source = (
        "Northstar Solar Ltd IPO opens 10 February and closes 12 February 2027. "
        "Listing is 10 February 2028."
    )

    result = validate_dates(
        {
            "opening_date": {
                "value": "2027-02-10",
                "status": "extracted",
                "evidence": "opens 10 February",
                "message": None,
            }
        },
        source,
    )

    assert result["fields"]["opening_date"]["value"] is None
    assert result["fields"]["opening_date"]["status"] == "uncertain"


# New regression tests


def test_ambiguous_date_makes_validation_invalid():
    result = validate_dates(
        {
            "opening_date": {
                "value": "2027-04-03",
                "status": "extracted",
                "evidence": "opens 03/04/2027",
                "message": None,
            }
        },
        "IPO opens 03/04/2027 and closes 6 April 2027.",
    )

    assert result["fields"]["opening_date"]["value"] is None
    assert result["fields"]["opening_date"]["status"] == "ambiguous"
    assert result["validation"]["valid"] is False


def test_conflicting_closing_dates_make_validation_invalid():
    result = validate_dates(
        {
            "closing_date": {
                "value": "2027-02-12",
                "status": "extracted",
                "evidence": "closes 12 February 2027",
                "message": None,
            }
        },
        ("IPO closes 12 February 2027. A correction says closing date is 13 February 2027."),
    )

    assert result["fields"]["closing_date"]["value"] is None
    assert result["fields"]["closing_date"]["status"] == "contradictory"
    assert result["validation"]["valid"] is False


def test_multiple_chronology_violations_make_validation_invalid():
    source = (
        "IPO opens 10 May 2027 and closes 12 May 2027. "
        "Allotment is 11 May, refund 10 May, and listing 10 May 2027."
    )

    fields = {
        "opening_date": ("2027-05-10", "opens 10 May 2027"),
        "closing_date": ("2027-05-12", "closes 12 May 2027"),
        "allotment_date": ("2027-05-11", "Allotment is 11 May"),
        "refund_date": ("2027-05-10", "refund 10 May"),
        "listing_date": ("2027-05-10", "listing 10 May 2027"),
    }

    result = validate_dates(
        {
            name: {
                "value": value,
                "status": "extracted",
                "evidence": evidence,
                "message": None,
            }
            for name, (value, evidence) in fields.items()
        },
        source,
    )

    assert result["validation"]["valid"] is False
    assert all(result["fields"][name]["value"] is None for name in fields)
