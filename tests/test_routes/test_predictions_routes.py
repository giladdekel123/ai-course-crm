FAKE_PREDICTIONS = [
    {
        "lead_id": 1, "name": "Priya Nair", "course_name": "AI Product Management",
        "status": "Interested", "probability": 91.0, "priority": "High",
        "top_factors": [{"label": "Source: Referral", "direction": "positive"}],
    },
]

FAKE_METRICS = {
    "accuracy": 0.6, "precision": 0.56, "recall": 0.44, "f1": 0.49, "roc_auc": 0.65,
    "n_train": 560, "n_test": 140, "n_total": 700, "converted_rate": 0.44,
    "trained_at": "2026-09-15T12:32:02+00:00",
}


def test_predictions_renders_scored_leads(client, monkeypatch):
    monkeypatch.setattr("app.services.ml_service.predict_for_active_leads", lambda c: FAKE_PREDICTIONS)
    monkeypatch.setattr("app.services.ml_service.get_model_metrics", lambda: FAKE_METRICS)

    response = client.get("/predictions/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Priya Nair" in body
    assert "91.0%" in body
    assert "Source: Referral" in body


def test_predictions_renders_empty_state_with_no_active_leads(client, monkeypatch):
    monkeypatch.setattr("app.services.ml_service.predict_for_active_leads", lambda c: [])
    monkeypatch.setattr("app.services.ml_service.get_model_metrics", lambda: FAKE_METRICS)

    response = client.get("/predictions/")

    assert response.status_code == 200
    assert "No active leads to score." in response.get_data(as_text=True)
