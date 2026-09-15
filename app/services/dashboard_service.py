from app.constants import LEAD_STATUSES
from app.repositories import leads_repo, registrations_repo
from app.services import courses_service


def get_dashboard_stats(client):
    status_counts = leads_repo.counts_by_status(client)
    total_leads = sum(status_counts.values())
    total_converted = status_counts.get("Converted", 0)

    pipeline_by_status = [
        {"status": status, "count": status_counts.get(status, 0)} for status in LEAD_STATUSES
    ]

    source_counts = leads_repo.counts_by_source(client)
    lead_sources = [
        {"source": source, "count": count}
        for source, count in sorted(source_counts.items(), key=lambda item: -item[1])
    ]

    courses = courses_service.list_courses(client, active_only=True)

    registrations = registrations_repo.list_all_with_course(client)
    revenue_by_course = {}
    total_revenue = 0.0
    for reg in registrations:
        course = reg.get("courses") or {}
        course_name = course.get("course_name", "Unknown")
        amount = float(reg["amount_paid"])
        revenue_by_course[course_name] = revenue_by_course.get(course_name, 0.0) + amount
        total_revenue += amount

    return {
        "total_new": status_counts.get("New", 0),
        "total_interested": status_counts.get("Interested", 0),
        "total_converted": total_converted,
        "total_leads": total_leads,
        "conversion_rate": round(total_converted / total_leads * 100, 1) if total_leads else 0.0,
        "leads_requiring_follow_up": status_counts.get("Follow-up", 0),
        "pipeline_by_status": pipeline_by_status,
        "lead_sources": lead_sources,
        "courses": courses,
        "revenue_by_course": sorted(
            ({"course_name": name, "revenue": round(amount, 2)} for name, amount in revenue_by_course.items()),
            key=lambda item: -item["revenue"],
        ),
        "total_revenue": round(total_revenue, 2),
    }
