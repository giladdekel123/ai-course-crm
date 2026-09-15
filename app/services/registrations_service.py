from app.repositories import registrations_repo


def create_registration(client, lead_id, course_id, enrollment_date, amount_paid, payment_method):
    return registrations_repo.create(client, {
        "lead_id": lead_id,
        "course_id": course_id,
        "enrollment_date": enrollment_date,
        "amount_paid": amount_paid,
        "payment_method": payment_method,
    })
