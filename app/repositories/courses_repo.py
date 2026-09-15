def list_all(client, active_only=False):
    query = client.table("courses").select("*")
    if active_only:
        query = query.eq("is_active", True)
    return query.order("start_date").execute().data


def get_by_id(client, course_id):
    response = client.table("courses").select("*").eq("id", course_id).single().execute()
    return response.data


def create(client, data):
    response = client.table("courses").insert(data).execute()
    return response.data[0]


def update(client, course_id, data):
    response = client.table("courses").update(data).eq("id", course_id).execute()
    return response.data[0]


def archive(client, course_id):
    return update(client, course_id, {"is_active": False})


def enrolled_counts_by_course(client):
    rows = client.table("registrations").select("course_id").execute().data
    counts = {}
    for row in rows:
        counts[row["course_id"]] = counts.get(row["course_id"], 0) + 1
    return counts


def interested_counts_by_course(client, active_statuses):
    rows = (
        client.table("leads")
        .select("course_interest_id")
        .in_("status", active_statuses)
        .not_.is_("course_interest_id", "null")
        .execute()
        .data
    )
    counts = {}
    for row in rows:
        counts[row["course_interest_id"]] = counts.get(row["course_interest_id"], 0) + 1
    return counts
