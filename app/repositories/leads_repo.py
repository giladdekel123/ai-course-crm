LEAD_SELECT_WITH_COURSE = "*,courses(id,course_name,delivery_format)"


def list_all(client, status=None, source=None, search=None):
    query = client.table("leads").select(LEAD_SELECT_WITH_COURSE)
    if status:
        query = query.eq("status", status)
    if source:
        query = query.eq("source", source)
    if search:
        like = f"%{search}%"
        query = query.or_(f"name.ilike.{like},email.ilike.{like},phone.ilike.{like}")
    return query.order("created_at", desc=True).execute().data


def get_by_id(client, lead_id):
    response = (
        client.table("leads")
        .select(LEAD_SELECT_WITH_COURSE)
        .eq("id", lead_id)
        .single()
        .execute()
    )
    return response.data


def create(client, data):
    response = client.table("leads").insert(data).execute()
    return response.data[0]


def update(client, lead_id, data):
    response = client.table("leads").update(data).eq("id", lead_id).execute()
    return response.data[0]


def update_status(client, lead_id, status):
    return update(client, lead_id, {"status": status})


def list_active_with_course(client, active_statuses):
    return (
        client.table("leads")
        .select("*,courses(course_name,delivery_format)")
        .in_("status", active_statuses)
        .execute()
        .data
    )


def counts_by_status(client):
    rows = client.table("leads").select("status").execute().data
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return counts


def counts_by_source(client):
    rows = client.table("leads").select("source").execute().data
    counts = {}
    for row in rows:
        source = row["source"] or "Unknown"
        counts[source] = counts.get(source, 0) + 1
    return counts
