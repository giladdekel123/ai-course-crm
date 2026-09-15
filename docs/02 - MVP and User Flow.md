## MVP

The MVP will provide one complete workflow from a new lead to a paid course registration.

### Core Features

- Create and manage leads
- Create and edit courses
- Track lead status
- Connect leads with courses they are interested in
- Convert a lead into a registration after enrollment and payment
- Store the data in Supabase
- Dashboard for monitoring courses, leads, registrations and revenue
- Machine Learning prediction of the probability that a lead will purchase a course

## Lead Status Workflow

New → Contacted → Follow-up → Interested → Converted

A lead can also become:

Not Interested

"Converted" means that the lead has enrolled in a course and completed payment.

## End-to-End User Flow

1. A new lead is entered into the CRM.
2. The lead receives the status "New".
3. The administrator contacts the lead.
4. The status is updated as the lead moves through the sales process.
5. The ML model calculates the probability that the lead will purchase a course.
6. If the lead decides to enroll and completes payment, a registration is created.
7. The lead status changes to "Converted".
8. The dashboard automatically reflects the new registration.

## Main CRM Screens

- Dashboard
- Leads
- Courses
- ML Predictions

## Dashboard

The dashboard will show:

- Enrolled vs. interested for each course
- Lead pipeline by status
- Conversion rate
- Leads requiring follow-up
- New leads
- Lead sources
- Course capacity
- Revenue by course

## ML Predictions

The ML Predictions tab will show:

- Lead
- Course of interest
- Current status
- Predicted purchase probability
- Main factors behind the prediction
- Priority