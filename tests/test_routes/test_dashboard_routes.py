FAKE_STATS = {
    "total_new": 5, "total_interested": 3, "total_converted": 2, "total_leads": 10,
    "conversion_rate": 20.0, "leads_requiring_follow_up": 1,
    "pipeline_by_status": [{"status": "New", "count": 5}],
    "lead_sources": [{"source": "Referral", "count": 4}],
    "courses": [{"id": 1, "course_name": "AI Foundations", "capacity": 50, "enrolled_count": 10,
                 "interested_count": 5, "capacity_filled_pct": 20.0}],
    "revenue_by_course": [{"course_name": "AI Foundations", "revenue": 5000.0}],
    "total_revenue": 5000.0,
}


def test_dashboard_renders_with_real_stats(client, monkeypatch):
    monkeypatch.setattr("app.services.dashboard_service.get_dashboard_stats", lambda c: FAKE_STATS)

    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Dashboard" in body
    assert "AI Foundations" in body
    assert "20.0%" in body
