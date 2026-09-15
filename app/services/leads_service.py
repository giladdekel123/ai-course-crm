from app.constants import LEAD_STATUSES
from app.repositories import leads_repo
from app.services import registrations_service


def _flatten_course(lead):
    course = lead.pop("courses", None)
    lead["course_name"] = course["course_name"] if course else None
    lead["course_delivery_format"] = course["delivery_format"] if course else None
    return lead


def list_leads(client, status=None, source=None, search=None):
    leads = leads_repo.list_all(client, status=status, source=source, search=search)
    return [_flatten_course(lead) for lead in leads]


def get_lead(client, lead_id):
    lead = leads_repo.get_by_id(client, lead_id)
    return _flatten_course(lead) if lead else None


def create_lead(client, data):
    payload = {**data, "status": "New"}
    return leads_repo.create(client, payload)


def update_lead(client, lead_id, data):
    return leads_repo.update(client, lead_id, data)


def change_status(client, lead_id, status):
    if status not in LEAD_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    return leads_repo.update_status(client, lead_id, status)


def convert_lead(client, lead_id, course_id, enrollment_date, amount_paid, payment_method):
    registrations_service.create_registration(
        client, lead_id, course_id, enrollment_date, amount_paid, payment_method,
    )
    return leads_repo.update_status(client, lead_id, "Converted")
