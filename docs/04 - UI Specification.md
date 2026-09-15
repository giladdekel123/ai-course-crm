## Main Navigation

The CRM has four main screens:

1. Dashboard
2. Leads
3. Courses
4. ML Predictions

The UI should be a clean, modern, professional desktop interface for a course administrator or salesperson.

---

## 1. Dashboard

The Dashboard provides an overview of the AI course sales and enrollment activity.

It should show:

- Total new leads
- Total interested leads
- Total converted/enrolled leads
- Conversion rate
- Leads requiring follow-up
- Enrolled vs. interested leads for each course
- Course capacity and percentage filled
- Lead acquisition sources
- Revenue by course

Interested leads must remain distinct from enrolled students.

---

## 2. Leads

The Leads screen provides a searchable and filterable directory of all leads.

The main table should show:

- Name
- Phone
- Email
- Course Interest
- Status
- Source
- Created Date
- Actions

Valid statuses:

- New
- Contacted
- Follow-up
- Interested
- Converted
- Not Interested

Each lead must have:

- View action
- Edit action

The administrator must be able to create a new lead.

Search and filtering should be available.

---

## 3. Courses

The Courses screen allows the administrator to view and manage AI courses.

For each course show:

- Course Name
- Start Date
- Duration
- Price
- Capacity
- Enrolled
- Interested Leads

The administrator must be able to:

- Create a new course
- Edit an existing course

Interested leads are not the same as enrolled students.

---

## 4. ML Predictions

The ML Predictions screen predicts the probability that a lead will purchase/enroll in an AI course.

For each lead show:

- Lead Name
- Course of Interest
- Current Status
- Purchase Probability
- Priority: High, Medium, or Low
- Main Reasons Behind Prediction

Prediction explanations may use CRM information including:

- Age
- Occupation
- Education
- Technical Experience
- Reason for Interest
- Source
- Course Interest
- Current Lead Status

Useful model performance information such as model accuracy may also be displayed.

Any model accuracy, probability, precision, or other ML values shown in the Stitch prototype are demonstration values only. The implemented application must calculate these values from the actual ML model and project dataset.

---

## UI Reference

The UI concept was designed and reviewed using Google Stitch.

Stitch provides the visual reference, but this specification defines the required functionality. If the Stitch design and this specification conflict, this specification takes priority.