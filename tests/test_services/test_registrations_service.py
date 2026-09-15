from app.services import registrations_service


def test_create_registration_builds_expected_payload(monkeypatch):
    captured = {}

    def fake_create(client, data):
        captured.update(data)
        return {"id": 1, **data}

    monkeypatch.setattr("app.repositories.registrations_repo.create", fake_create)

    registrations_service.create_registration(
        object(), lead_id=1, course_id=2, enrollment_date="2026-01-01",
        amount_paid=999.0, payment_method="Credit Card",
    )

    assert captured == {
        "lead_id": 1,
        "course_id": 2,
        "enrollment_date": "2026-01-01",
        "amount_paid": 999.0,
        "payment_method": "Credit Card",
    }
