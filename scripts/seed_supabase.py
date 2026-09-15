"""Seed the Supabase database with the generated synthetic data.

Run after `scripts/generate_synthetic_data.py`. Loads SUPABASE_URL /
SUPABASE_SERVICE_KEY from .env and inserts courses, then leads, then
registrations - in that order, since leads/registrations reference the
real Supabase-assigned ids rather than the local synthetic ids used in
the CSVs. Refuses to run if the tables already have data, to avoid
double-seeding.
"""
import csv
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic"
BATCH_SIZE = 200


def read_csv(name):
    with (DATA_DIR / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def chunks(rows, size):
    for i in range(0, len(rows), size):
        yield rows[i:i + size]


def insert_in_batches(client, table, rows):
    inserted = []
    for batch in chunks(rows, BATCH_SIZE):
        response = client.table(table).insert(batch).execute()
        inserted.extend(response.data)
    return inserted


def seed_courses(client, rows):
    payload = [
        {
            "course_name": r["course_name"],
            "description": r["description"],
            "start_date": r["start_date"],
            "duration": r["duration"],
            "price": float(r["price"]),
            "capacity": int(r["capacity"]),
            "delivery_format": r["delivery_format"],
        }
        for r in rows
    ]
    inserted = insert_in_batches(client, "courses", payload)
    name_to_real_id = {row["course_name"]: row["id"] for row in inserted}
    return {r["course_id"]: name_to_real_id[r["course_name"]] for r in rows}


def seed_leads(client, rows, course_id_map):
    payload = [
        {
            "name": r["name"],
            "phone": r["phone"],
            "email": r["email"],
            "age": int(r["age"]),
            "city": r["city"],
            "occupation": r["occupation"],
            "education": r["education"],
            "technical_experience": r["technical_experience"],
            "reason_for_interest": r["reason_for_interest"],
            "source": r["source"],
            "status": r["status"],
            "course_interest_id": course_id_map[r["course_interest_id"]],
            "created_at": r["created_at"],
        }
        for r in rows
    ]
    inserted = insert_in_batches(client, "leads", payload)
    email_to_real_id = {row["email"]: row["id"] for row in inserted}
    return {r["lead_id"]: email_to_real_id[r["email"]] for r in rows}


def seed_registrations(client, rows, lead_id_map, course_id_map):
    payload = [
        {
            "lead_id": lead_id_map[r["lead_id"]],
            "course_id": course_id_map[r["course_id"]],
            "enrollment_date": r["enrollment_date"],
            "amount_paid": float(r["amount_paid"]),
            "payment_method": r["payment_method"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]
    insert_in_batches(client, "registrations", payload)


def table_counts(client):
    counts = {}
    for table in ("courses", "leads", "registrations"):
        response = client.table(table).select("id", count="exact").limit(1).execute()
        counts[table] = response.count
    return counts


def main():
    load_dotenv()
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    counts = table_counts(client)
    if any(counts.values()):
        print(f"Tables are not empty: {counts}")
        print("Refusing to seed on top of existing data. Truncate the tables first if you want to re-seed.")
        sys.exit(1)

    courses = read_csv("courses.csv")
    leads = read_csv("leads.csv")
    registrations = read_csv("registrations.csv")

    print(f"Seeding {len(courses)} courses...")
    course_id_map = seed_courses(client, courses)

    print(f"Seeding {len(leads)} leads...")
    lead_id_map = seed_leads(client, leads, course_id_map)

    print(f"Seeding {len(registrations)} registrations...")
    seed_registrations(client, registrations, lead_id_map, course_id_map)

    print(f"Done. Final row counts: {table_counts(client)}")


if __name__ == "__main__":
    main()
