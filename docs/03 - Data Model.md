## Data Model

The CRM will initially use three core tables:

1. Leads
2. Courses
3. Registrations

## Leads

Stores information about people who have shown interest in AI courses.

Fields:

- id
- name
- phone
- email
- age
- city
- occupation
- education
- technical_experience
- reason_for_interest
- source
- status
- created_at

### Lead Status Values

- New
- Contacted
- Follow-up
- Interested
- Converted
- Not Interested

## Courses

Stores information about the AI courses offered by the organization.

Fields:

- id
- course_name
- description
- start_date
- duration
- price
- capacity
- delivery_format

Possible delivery formats:

- In-person
- Online
- Hybrid

The administrator can create and edit courses from the CRM. Courses with historical registrations should be archived/deactivated rather than deleted.

## Registrations

A registration is created only after a lead has enrolled in a course and completed payment.

Fields:

- id
- lead_id
- course_id
- enrollment_date
- amount_paid
- payment_method

### Relationships

Each Registration belongs to one Lead.

Each Registration belongs to one Course.

A Lead becomes "Converted" when enrollment and payment are completed and a Registration is created.