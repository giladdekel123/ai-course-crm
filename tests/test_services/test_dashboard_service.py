from app.constants import LEAD_STATUSES
from app.services import dashboard_service


def _patch_common(monkeypatch, status_counts, source_counts, registrations, courses=None):
    monkeypatch.setattr("app.repositories.leads_repo.counts_by_status", lambda client: status_counts)
    monkeypatch.setattr("app.repositories.leads_repo.counts_by_source", lambda client: source_counts)
    monkeypatch.setattr(
        "app.repositories.registrations_repo.list_all_with_course", lambda client: registrations,
    )
    monkeypatch.setattr(
        "app.services.courses_service.list_courses",
        lambda client, active_only=False: courses or [],
    )


def test_conversion_rate_and_top_line_counts(monkeypatch):
    _patch_common(
        monkeypatch,
        status_counts={"New": 4, "Interested": 3, "Converted": 2, "Follow-up": 1},
        source_counts={},
        registrations=[],
    )

    stats = dashboard_service.get_dashboard_stats(object())

    assert stats["total_new"] == 4
    assert stats["total_interested"] == 3
    assert stats["total_converted"] == 2
    assert stats["leads_requiring_follow_up"] == 1
    assert stats["total_leads"] == 10
    assert stats["conversion_rate"] == 20.0


def test_conversion_rate_is_zero_with_no_leads_not_a_div_by_zero(monkeypatch):
    _patch_common(monkeypatch, status_counts={}, source_counts={}, registrations=[])

    stats = dashboard_service.get_dashboard_stats(object())

    assert stats["total_leads"] == 0
    assert stats["conversion_rate"] == 0.0


def test_pipeline_by_status_includes_every_status_even_when_zero(monkeypatch):
    _patch_common(monkeypatch, status_counts={"New": 5}, source_counts={}, registrations=[])

    stats = dashboard_service.get_dashboard_stats(object())

    statuses_present = {row["status"] for row in stats["pipeline_by_status"]}
    assert statuses_present == set(LEAD_STATUSES)
    counts = {row["status"]: row["count"] for row in stats["pipeline_by_status"]}
    assert counts["New"] == 5
    assert counts["Converted"] == 0


def test_lead_sources_sorted_descending_by_count(monkeypatch):
    _patch_common(
        monkeypatch,
        status_counts={},
        source_counts={"Referral": 3, "Website": 10, "Event": 5},
        registrations=[],
    )

    stats = dashboard_service.get_dashboard_stats(object())

    assert [row["source"] for row in stats["lead_sources"]] == ["Website", "Event", "Referral"]


def test_revenue_by_course_aggregates_and_sorts_descending(monkeypatch):
    registrations = [
        {"amount_paid": "500.00", "courses": {"course_name": "AI Foundations"}},
        {"amount_paid": "300.00", "courses": {"course_name": "AI Foundations"}},
        {"amount_paid": "1000.00", "courses": {"course_name": "MLOps"}},
    ]
    _patch_common(monkeypatch, status_counts={}, source_counts={}, registrations=registrations)

    stats = dashboard_service.get_dashboard_stats(object())

    assert stats["revenue_by_course"] == [
        {"course_name": "MLOps", "revenue": 1000.0},
        {"course_name": "AI Foundations", "revenue": 800.0},
    ]
    assert stats["total_revenue"] == 1800.0


def test_revenue_by_course_handles_missing_course_join(monkeypatch):
    registrations = [{"amount_paid": "250.00", "courses": None}]
    _patch_common(monkeypatch, status_counts={}, source_counts={}, registrations=registrations)

    stats = dashboard_service.get_dashboard_stats(object())

    assert stats["revenue_by_course"] == [{"course_name": "Unknown", "revenue": 250.0}]
