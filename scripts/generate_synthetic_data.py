"""Generate synthetic courses, leads, and registrations for AI Course CRM.

Historical leads get a terminal status (Converted / Not Interested) driven by a
hidden propensity-to-convert score built from a few features plus noise, so the
ML model trained on them later has real signal to find. Active-pipeline leads
are left with a non-terminal status and no registration - they're what the ML
Predictions screen scores.
"""
import csv
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from faker import Faker

from app.constants import (
    ACTIVE_LEAD_STATUSES,
    DELIVERY_FORMATS,
    EDUCATION_LEVELS,
    OCCUPATIONS,
    PAYMENT_METHODS,
    REASONS_FOR_INTEREST,
    SOURCES,
    TECHNICAL_EXPERIENCE_LEVELS,
)

SEED = 42
ANCHOR_DATE = date(2026, 9, 15)

N_COURSES = 12
N_HISTORICAL_LEADS = 700
N_ACTIVE_LEADS = 100

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic"

DURATIONS = ["4 weeks", "6 weeks", "8 weeks", "10 weeks", "12 weeks", "3 months", "6 months"]
COURSE_TOPICS = [
    "AI Foundations", "Machine Learning Bootcamp", "Deep Learning Intensive",
    "Applied Data Science", "Generative AI for Business", "Computer Vision Fundamentals",
    "NLP & Large Language Models", "AI Product Management", "MLOps & Deployment",
    "AI for Healthcare", "AI for Finance", "Prompt Engineering Masterclass",
    "Reinforcement Learning Essentials", "AI Ethics & Governance", "Robotics & AI",
]

EDUCATION_WEIGHTS_DIST = [0.15, 0.45, 0.28, 0.07, 0.05]
TECH_EXPERIENCE_DIST = [0.25, 0.35, 0.28, 0.12]
PAYMENT_METHOD_WEIGHTS = [0.45, 0.30, 0.20, 0.05]

ACTIVE_STATUS_WEIGHTS = [0.35, 0.30, 0.20, 0.15]

# Hidden ground-truth weights used only to assign historical outcomes -
# the ML model trained later has to (re)discover this signal from data alone.
TECH_EXPERIENCE_SCORE = {"None": 0, "Beginner": 1, "Intermediate": 2, "Advanced": 3}
EDUCATION_WEIGHT = {"High School": 0.0, "Bachelor's": 0.2, "Master's": 0.4, "PhD": 0.5, "Other": 0.0}
OCCUPATION_WEIGHT = {
    "Student": -0.1, "Software Engineer": 0.3, "Data Analyst": 0.3,
    "Product Manager": 0.2, "Business Owner": 0.4, "Marketing Professional": 0.1,
    "Finance Professional": 0.1, "Teacher": 0.0, "Healthcare Professional": 0.0,
    "Unemployed": -0.2, "Other": 0.0,
}
REASON_WEIGHT = {
    "Career change": 0.8, "Skill upgrade": 0.4, "Academic interest": 0.2,
    "Employer requirement": 1.0, "Starting a business": 0.6, "General curiosity": -0.3,
}
SOURCE_WEIGHT = {
    "Website": 0.3, "Social Media": 0.1, "Referral": 1.2, "Event": 0.5,
    "Advertisement": -0.1, "Partner Organization": 0.7, "Cold Outreach": -0.5,
}
DELIVERY_FORMAT_WEIGHT = {"Online": 0.1, "Hybrid": 0.05, "In-person": -0.05}


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def generate_courses(rng):
    rows = []
    topics = list(rng.permutation(COURSE_TOPICS)[:N_COURSES])
    for i, topic in enumerate(topics, start=1):
        rows.append({
            "course_id": i,
            "course_name": str(topic),
            "description": f"A hands-on {topic.lower()} program for working professionals.",
            "start_date": (ANCHOR_DATE + timedelta(days=int(rng.integers(-150, 150)))).isoformat(),
            "duration": str(rng.choice(DURATIONS)),
            "price": round(float(rng.uniform(299, 2999)), 2),
            "capacity": int(rng.integers(15, 61)),
            "delivery_format": str(rng.choice(DELIVERY_FORMATS)),
        })
    return rows


def build_lead_profile(rng, fake, course_row):
    age = int(np.clip(rng.normal(32, 9), 18, 65))
    education = str(rng.choice(EDUCATION_LEVELS, p=EDUCATION_WEIGHTS_DIST))
    technical_experience = str(rng.choice(TECHNICAL_EXPERIENCE_LEVELS, p=TECH_EXPERIENCE_DIST))
    occupation = str(rng.choice(OCCUPATIONS))
    reason_for_interest = str(rng.choice(REASONS_FOR_INTEREST))
    source = str(rng.choice(SOURCES))

    propensity = (
        -1.7
        + TECH_EXPERIENCE_SCORE[technical_experience] * 0.35
        + EDUCATION_WEIGHT[education]
        + OCCUPATION_WEIGHT[occupation]
        + REASON_WEIGHT[reason_for_interest]
        + SOURCE_WEIGHT[source]
        + DELIVERY_FORMAT_WEIGHT[course_row["delivery_format"]]
        - abs(age - 32) * 0.01
        + rng.normal(0, 1.0)
    )
    probability = sigmoid(propensity)

    profile = {
        "name": fake.name(),
        "phone": fake.phone_number(),
        "email": fake.unique.email(),
        "age": age,
        "city": fake.city(),
        "occupation": occupation,
        "education": education,
        "technical_experience": technical_experience,
        "reason_for_interest": reason_for_interest,
        "source": source,
    }
    return profile, probability


def generate_historical_leads(rng, fake, courses):
    leads, registrations = [], []
    lead_id = 1
    registration_id = 1
    for _ in range(N_HISTORICAL_LEADS):
        course = courses[int(rng.integers(0, len(courses)))]
        profile, probability = build_lead_profile(rng, fake, course)
        converted = rng.random() < probability
        status = "Converted" if converted else "Not Interested"
        created_at = ANCHOR_DATE - timedelta(days=int(rng.integers(30, 270)))

        leads.append({
            "lead_id": lead_id,
            **profile,
            "status": status,
            "course_interest_id": course["course_id"],
            "created_at": created_at.isoformat(),
        })

        if converted:
            enrollment_date = created_at + timedelta(days=int(rng.integers(3, 21)))
            amount_paid = max(round(course["price"] * float(rng.uniform(0.85, 1.05)), 2), 0.0)
            registrations.append({
                "registration_id": registration_id,
                "lead_id": lead_id,
                "course_id": course["course_id"],
                "enrollment_date": enrollment_date.isoformat(),
                "amount_paid": amount_paid,
                "payment_method": str(rng.choice(PAYMENT_METHODS, p=PAYMENT_METHOD_WEIGHTS)),
                "created_at": enrollment_date.isoformat(),
            })
            registration_id += 1

        lead_id += 1

    return leads, registrations, lead_id


def generate_active_leads(rng, fake, courses, start_lead_id):
    leads = []
    lead_id = start_lead_id
    for _ in range(N_ACTIVE_LEADS):
        course = courses[int(rng.integers(0, len(courses)))]
        profile, _probability = build_lead_profile(rng, fake, course)
        status = str(rng.choice(ACTIVE_LEAD_STATUSES, p=ACTIVE_STATUS_WEIGHTS))
        created_at = ANCHOR_DATE - timedelta(days=int(rng.integers(0, 45)))

        leads.append({
            "lead_id": lead_id,
            **profile,
            "status": status,
            "course_interest_id": course["course_id"],
            "created_at": created_at.isoformat(),
        })
        lead_id += 1

    return leads


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    rng = np.random.default_rng(SEED)
    fake = Faker()
    Faker.seed(SEED)

    courses = generate_courses(rng)
    historical_leads, registrations, next_lead_id = generate_historical_leads(rng, fake, courses)
    active_leads = generate_active_leads(rng, fake, courses, next_lead_id)
    all_leads = historical_leads + active_leads

    write_csv(
        OUTPUT_DIR / "courses.csv", courses,
        ["course_id", "course_name", "description", "start_date", "duration",
         "price", "capacity", "delivery_format"],
    )
    write_csv(
        OUTPUT_DIR / "leads.csv", all_leads,
        ["lead_id", "name", "phone", "email", "age", "city", "occupation", "education",
         "technical_experience", "reason_for_interest", "source", "status",
         "course_interest_id", "created_at"],
    )
    write_csv(
        OUTPUT_DIR / "registrations.csv", registrations,
        ["registration_id", "lead_id", "course_id", "enrollment_date",
         "amount_paid", "payment_method", "created_at"],
    )

    n_converted = sum(1 for lead in historical_leads if lead["status"] == "Converted")
    n_not_interested = len(historical_leads) - n_converted
    print(f"Courses: {len(courses)}")
    print(f"Historical leads: {len(historical_leads)} "
          f"(Converted: {n_converted}, Not Interested: {n_not_interested})")
    print(f"Active pipeline leads: {len(active_leads)}")
    print(f"Registrations: {len(registrations)}")
    print(f"Written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
