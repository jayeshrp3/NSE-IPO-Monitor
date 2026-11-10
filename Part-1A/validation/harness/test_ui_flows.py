"""Browser-visible page and explicit deletion-confirmation tests."""

import re
from datetime import date, timedelta


def test_pages_load_and_delete_cancel_sends_no_request(browser, base_url):
    page = browser.new_page()
    response = page.goto(f"{base_url}/")
    assert response is not None and response.status == 200
    assert page.get_by_role("heading", name="IPO schedule").is_visible()
    assert page.locator('link[href*="/static/css/styles.css"]').count() == 1
    assert page.locator('script[src*="/static/js/app.js"]').count() == 1

    form_page = page.goto(f"{base_url}/ipos/new")
    assert form_page is not None and form_page.status == 200
    assert page.get_by_role("heading", name="Add IPO").is_visible()

    created = page.request.post(
        f"{base_url}/api/ipos",
        data={
            "company_name": "Confirm deletion",
            "opening_date": (date.today() + timedelta(days=10)).isoformat(),
            "closing_date": (date.today() + timedelta(days=12)).isoformat(),
        },
    )
    assert created.status == 201
    record = created.json()
    detail = page.goto(f"{base_url}/ipos/{record['id']}")
    assert detail is not None and detail.status == 200
    assert page.get_by_role("heading", name="Confirm deletion").is_visible()

    delete_requests = []
    page.on(
        "request",
        lambda request: delete_requests.append(request.url)
        if request.method == "DELETE"
        else None,
    )
    page.on("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Delete").click()
    assert delete_requests == []
    assert page.request.get(f"{base_url}/api/ipos/{record['id']}").status == 200
    page.close()


def test_delete_confirmation_accepts_and_deletes(browser, base_url):
    page = browser.new_page()
    created = page.request.post(
        f"{base_url}/api/ipos",
        data={
            "company_name": "Confirmed deletion",
            "opening_date": (date.today() + timedelta(days=20)).isoformat(),
            "closing_date": (date.today() + timedelta(days=22)).isoformat(),
        },
    )
    assert created.status == 201
    record_id = created.json()["id"]
    page.on("dialog", lambda dialog: dialog.accept())
    page.goto(f"{base_url}/ipos/{record_id}")
    page.get_by_role("button", name="Delete").click()
    page.wait_for_url(f"{base_url}/")
    assert page.request.get(f"{base_url}/api/ipos/{record_id}").status == 404
    page.close()


def test_form_submission_and_optional_date_clear_flow(browser, base_url):
    page = browser.new_page()
    page.goto(f"{base_url}/ipos/new")
    page.get_by_label("Company name").fill("Browser-created IPO")
    page.get_by_label("Opening date").fill(
        (date.today() + timedelta(days=10)).isoformat()
    )
    page.get_by_label("Closing date").fill(
        (date.today() + timedelta(days=12)).isoformat()
    )
    page.get_by_role("button", name="Save IPO").click()
    page.wait_for_url(re.compile(f"{re.escape(base_url)}/ipos/\\d+$"))
    record_id = page.url.rsplit("/", 1)[-1]
    assert page.get_by_role("heading", name="Browser-created IPO").is_visible()

    original_listing = date.today() + timedelta(days=20)
    created = page.request.put(
        f"{base_url}/api/ipos/{record_id}",
        data={"listing_date": original_listing.isoformat()},
    )
    assert created.status == 200

    page.goto(f"{base_url}/ipos/{record_id}/edit")
    page.get_by_role("button", name="Save IPO").click()
    page.wait_for_url(f"**/ipos/{record_id}")
    detail = page.request.get(f"{base_url}/api/ipos/{record_id}").json()
    assert detail["listing_date"] == original_listing.isoformat()

    page.goto(f"{base_url}/ipos/{record_id}/edit")
    page.get_by_label("Clear", exact=False).check()
    page.get_by_role("button", name="Save IPO").click()
    page.wait_for_url(f"**/ipos/{record_id}")
    detail = page.request.get(f"{base_url}/api/ipos/{record_id}").json()
    assert detail["listing_date"] is None
    page.close()


def test_expired_deadline_is_clear_in_detail_page(browser, base_url):
    page = browser.new_page()
    response = page.request.post(
        f"{base_url}/api/ipos",
        data={
            "company_name": "Expired UI record",
            "opening_date": "2020-01-01",
            "closing_date": "2020-01-02",
        },
    )
    assert response.status == 201
    record_id = response.json()["id"]
    expired_days = response.json()["expired_days"]
    page.goto(f"{base_url}/ipos/{record_id}")
    assert page.get_by_text(f"Deadline expired {expired_days} days ago").is_visible()
    assert page.get_by_text(f"Expired {expired_days} days ago", exact=True).is_visible()
    page.close()
