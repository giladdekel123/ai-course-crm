import pytest

from app.services import leads_service


def test_list_leads_flattens_course_and_forwards_filters(monkeypatch):
    captured = {}

    def fake_list_all(client, status=None, source=None, search=None):
        captured.update(status=status, source=source, search=search)
        return [
            {"id": 1, "name": "Ada Lovelace", "courses": {"course_name": "AI Foundations", "delivery_format": "Online"}},
            {"id": 2, "name": "Alan Turing", "courses": None},
        ]

    monkeypatch.setattr("app.repositories.leads_repo.list_all", fake_list_all)

    leads = leads_service.list_leads(object(), status="New", source="Referral", search="ada")

    assert captured == {"status": "New", "source": "Referral", "search": "ada"}
    assert leads[0]["course_name"] == "AI Foundations"
    assert leads[0]["course_delivery_format"] == "Online"
    assert "courses" not in leads[0]
    assert leads[1]["course_name"] is None
    assert leads[1]["course_delivery_format"] is None


def test_get_lead_flattens_course(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.leads_repo.get_by_id",
        lambda client, lead_id: {"id": lead_id, "name": "Grace Hopper", "courses": {"course_name": "MLOps", "delivery_format": "Hybrid"}},
    )

    lead = leads_service.get_lead(object(), 42)

    assert lead["course_name"] == "MLOps"
    assert "courses" not in lead


def test_get_lead_returns_none_when_not_found(monkeypatch):
    monkeypatch.setattr("app.repositories.leads_repo.get_by_id", lambda client, lead_id: None)

    assert leads_service.get_lead(object(), 999) is None


def test_create_lead_always_forces_new_status(monkeypatch):
    captured = {}

    def fake_create(client, payload):
        captured.update(payload)
        return {"id": 1, **payload}

    monkeypatch.setattr("app.repositories.leads_repo.create", fake_create)

    leads_service.create_lead(object(), {"name": "New Lead", "status": "Converted"})

    # Even if a caller sneaks a status into the input data, every new lead starts as New.
    assert captured["status"] == "New"
    assert captured["name"] == "New Lead"


def test_change_status_rejects_invalid_status():
    with pytest.raises(ValueError):
        leads_service.change_status(object(), 1, "Definitely Not A Status")


def test_change_status_updates_valid_status(monkeypatch):
    captured = {}

    def fake_update_status(client, lead_id, status):
        captured.update(lead_id=lead_id, status=status)

    monkeypatch.setattr("app.repositories.leads_repo.update_status", fake_update_status)

    leads_service.change_status(object(), 7, "Interested")

    assert captured == {"lead_id": 7, "status": "Interested"}


def test_convert_lead_creates_registration_then_marks_converted(monkeypatch):
    calls = []

    def fake_create_registration(client, lead_id, course_id, enrollment_date, amount_paid, payment_method):
        calls.append(("create_registration", lead_id, course_id, enrollment_date, amount_paid, payment_method))

    def fake_update_status(client, lead_id, status):
        calls.append(("update_status", lead_id, status))

    monkeypatch.setattr("app.services.registrations_service.create_registration", fake_create_registration)
    monkeypatch.setattr("app.repositories.leads_repo.update_status", fake_update_status)

    leads_service.convert_lead(object(), 5, 3, "2026-01-01", 999.0, "Credit Card")

    assert calls == [
        ("create_registration", 5, 3, "2026-01-01", 999.0, "Credit Card"),
        ("update_status", 5, "Converted"),
    ]
