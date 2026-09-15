FAKE_COURSES = [{"id": 1, "course_name": "AI Foundations", "capacity": 50, "enrolled_count": 0,
                 "interested_count": 0, "capacity_filled_pct": 0.0}]

FAKE_LEAD = {
    "id": 7, "name": "Ada Lovelace", "phone": "555-0100", "email": "ada@example.com",
    "age": 30, "city": "London", "occupation": "Software Engineer", "education": "Bachelor's",
    "technical_experience": "Advanced", "reason_for_interest": "Career change", "source": "Referral",
    "status": "Interested", "course_interest_id": 1, "course_name": "AI Foundations",
    "course_delivery_format": "Online", "created_at": "2026-01-01T00:00:00",
}

VALID_LEAD_FORM_DATA = {
    "name": "New Lead", "phone": "", "email": "", "age": "", "city": "",
    "occupation": "Software Engineer", "education": "Bachelor's",
    "technical_experience": "Advanced", "reason_for_interest": "Career change",
    "source": "Referral", "course_interest_id": "1",
}


def _mock_courses(monkeypatch, courses=FAKE_COURSES):
    monkeypatch.setattr("app.services.courses_service.list_courses", lambda c, active_only=False: courses)


def test_list_leads_renders_and_forwards_query_filters(client, monkeypatch):
    captured = {}

    def fake_list_leads(c, status=None, source=None, search=None):
        captured.update(status=status, source=source, search=search)
        return [FAKE_LEAD]

    monkeypatch.setattr("app.services.leads_service.list_leads", fake_list_leads)

    response = client.get("/leads/?status=Interested&source=Referral&q=Ada")

    assert response.status_code == 200
    assert captured == {"status": "Interested", "source": "Referral", "search": "Ada"}
    assert "Ada Lovelace" in response.get_data(as_text=True)


def test_new_lead_get_renders_form(client, monkeypatch):
    _mock_courses(monkeypatch)

    response = client.get("/leads/new")

    assert response.status_code == 200
    assert "New Lead" in response.get_data(as_text=True)


def test_new_lead_post_creates_and_redirects(client, monkeypatch):
    _mock_courses(monkeypatch)
    captured = {}

    def fake_create_lead(c, data):
        captured.update(data)
        return {"id": 55, "name": data["name"]}

    monkeypatch.setattr("app.services.leads_service.create_lead", fake_create_lead)

    response = client.post("/leads/new", data=VALID_LEAD_FORM_DATA, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == "/leads/55"
    assert captured["name"] == "New Lead"
    assert captured["course_interest_id"] == 1


def test_new_lead_post_missing_required_field_reshows_form(client, monkeypatch):
    _mock_courses(monkeypatch)
    monkeypatch.setattr(
        "app.services.leads_service.create_lead",
        lambda c, data: (_ for _ in ()).throw(AssertionError("should not be called")),
    )

    data = {**VALID_LEAD_FORM_DATA, "name": ""}
    response = client.post("/leads/new", data=data, follow_redirects=False)

    assert response.status_code == 200  # re-renders the form, no redirect
    assert "This field is required" in response.get_data(as_text=True)


def test_view_lead_renders_profile(client, monkeypatch):
    _mock_courses(monkeypatch)
    monkeypatch.setattr("app.services.leads_service.get_lead", lambda c, lead_id: FAKE_LEAD)

    response = client.get("/leads/7")

    assert response.status_code == 200
    assert "Ada Lovelace" in response.get_data(as_text=True)


def test_view_lead_404s_when_not_found(client, monkeypatch):
    _mock_courses(monkeypatch)
    monkeypatch.setattr("app.services.leads_service.get_lead", lambda c, lead_id: None)

    response = client.get("/leads/999")

    assert response.status_code == 404


def test_view_lead_hides_convert_panel_for_terminal_status(client, monkeypatch):
    _mock_courses(monkeypatch)
    converted_lead = {**FAKE_LEAD, "status": "Converted"}
    monkeypatch.setattr("app.services.leads_service.get_lead", lambda c, lead_id: converted_lead)

    response = client.get("/leads/7")
    body = response.get_data(as_text=True)

    assert "Convert to Registration" not in body


def test_view_lead_shows_convert_panel_for_active_status(client, monkeypatch):
    _mock_courses(monkeypatch)
    monkeypatch.setattr("app.services.leads_service.get_lead", lambda c, lead_id: FAKE_LEAD)

    response = client.get("/leads/7")
    body = response.get_data(as_text=True)

    assert "Convert to Registration" in body


def test_edit_lead_get_404s_when_not_found(client, monkeypatch):
    _mock_courses(monkeypatch)
    monkeypatch.setattr("app.services.leads_service.get_lead", lambda c, lead_id: None)

    response = client.get("/leads/999/edit")

    assert response.status_code == 404


def test_edit_lead_post_updates_and_redirects(client, monkeypatch):
    _mock_courses(monkeypatch)
    monkeypatch.setattr("app.services.leads_service.get_lead", lambda c, lead_id: FAKE_LEAD)
    captured = {}

    def fake_update_lead(c, lead_id, data):
        captured.update(lead_id=lead_id, data=data)

    monkeypatch.setattr("app.services.leads_service.update_lead", fake_update_lead)

    response = client.post("/leads/7/edit", data=VALID_LEAD_FORM_DATA, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == "/leads/7"
    assert captured["lead_id"] == 7


def test_update_status_calls_service_and_redirects(client, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "app.services.leads_service.change_status",
        lambda c, lead_id, status: captured.update(lead_id=lead_id, status=status),
    )

    response = client.post("/leads/7/status", data={"status": "Contacted"}, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == "/leads/7"
    assert captured == {"lead_id": 7, "status": "Contacted"}


def test_convert_lead_calls_service_and_redirects(client, monkeypatch):
    _mock_courses(monkeypatch)
    captured = {}

    def fake_convert(c, lead_id, course_id, enrollment_date, amount_paid, payment_method):
        captured.update(
            lead_id=lead_id, course_id=course_id, enrollment_date=enrollment_date,
            amount_paid=amount_paid, payment_method=payment_method,
        )

    monkeypatch.setattr("app.services.leads_service.convert_lead", fake_convert)

    response = client.post(
        "/leads/7/convert",
        data={
            "course_id": "1", "enrollment_date": "2026-02-01",
            "amount_paid": "999.00", "payment_method": "Credit Card",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert captured == {
        "lead_id": 7, "course_id": 1, "enrollment_date": "2026-02-01",
        "amount_paid": 999.0, "payment_method": "Credit Card",
    }


def test_convert_lead_with_invalid_data_does_not_call_service(client, monkeypatch):
    _mock_courses(monkeypatch)
    monkeypatch.setattr(
        "app.services.leads_service.convert_lead",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not be called")),
    )

    response = client.post(
        "/leads/7/convert",
        data={"course_id": "1", "enrollment_date": "", "amount_paid": "", "payment_method": "Credit Card"},
        follow_redirects=False,
    )

    assert response.status_code == 302  # redirects back to the lead with a flash error, not a crash
