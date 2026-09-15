def create(client, data):
    response = client.table("registrations").insert(data).execute()
    return response.data[0]


def list_all_with_course(client):
    return (
        client.table("registrations")
        .select("*,courses(course_name)")
        .execute()
        .data
    )
