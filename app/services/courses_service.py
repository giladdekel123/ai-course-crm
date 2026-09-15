from app.constants import ACTIVE_LEAD_STATUSES
from app.repositories import courses_repo


def list_courses(client, active_only=False):
    courses = courses_repo.list_all(client, active_only=active_only)
    enrolled_counts = courses_repo.enrolled_counts_by_course(client)
    interested_counts = courses_repo.interested_counts_by_course(client, ACTIVE_LEAD_STATUSES)

    for course in courses:
        enrolled = enrolled_counts.get(course["id"], 0)
        interested = interested_counts.get(course["id"], 0)
        capacity = course["capacity"] or 0
        course["enrolled_count"] = enrolled
        course["interested_count"] = interested
        course["capacity_filled_pct"] = round(enrolled / capacity * 100, 1) if capacity else 0.0

    return courses


def get_course(client, course_id):
    return courses_repo.get_by_id(client, course_id)


def create_course(client, data):
    return courses_repo.create(client, data)


def update_course(client, course_id, data):
    return courses_repo.update(client, course_id, data)


def archive_course(client, course_id):
    return courses_repo.archive(client, course_id)
