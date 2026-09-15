FAKE_COURSE = {
    "id": 3, "course_name": "AI Foundations", "description": "Intro to AI",
    "start_date": "2026-06-01", "duration": "8 weeks", "price": 999.0, "capacity": 50,
    "delivery_format": "Online", "is_active": True, "enrolled_count": 10,
    "interested_count": 5, "capacity_filled_pct": 20.0,
}

VALID_COURSE_FORM_DATA = {
    "course_name": "New AI Course", "description": "Great course", "start_date": "2026-09-01",
    "duration": "6 weeks", "price": "1200.00", "capacity": "40", "delivery_format": "Online",
}


def test_list_courses_renders(client, monkeypatch):
    monkeypatch.setattr("app.services.courses_service.list_courses", lambda c, active_only=False: [FAKE_COURSE])

    response = client.get("/courses/")

    assert response.status_code == 200
    assert "AI Foundations" in response.get_data(as_text=True)


def test_new_course_get_renders_form(client):
    response = client.get("/courses/new")

    assert response.status_code == 200
    assert "New Course" in response.get_data(as_text=True)


def test_new_course_post_creates_and_redirects(client, monkeypatch):
    captured = {}

    def fake_create_course(c, data):
        captured.update(data)
        return {"id": 9, **data}

    monkeypatch.setattr("app.services.courses_service.create_course", fake_create_course)

    response = client.post("/courses/new", data=VALID_COURSE_FORM_DATA, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == "/courses/"
    assert captured["course_name"] == "New AI Course"
    assert captured["price"] == 1200.0
    assert captured["capacity"] == 40


def test_edit_course_get_prefills_form(client, monkeypatch):
    monkeypatch.setattr("app.services.courses_service.get_course", lambda c, course_id: FAKE_COURSE)

    response = client.get("/courses/3/edit")

    assert response.status_code == 200
    assert 'value="AI Foundations"' in response.get_data(as_text=True)


def test_edit_course_get_404s_when_not_found(client, monkeypatch):
    monkeypatch.setattr("app.services.courses_service.get_course", lambda c, course_id: None)

    response = client.get("/courses/999/edit")

    assert response.status_code == 404


def test_edit_course_post_updates_and_redirects(client, monkeypatch):
    monkeypatch.setattr("app.services.courses_service.get_course", lambda c, course_id: FAKE_COURSE)
    captured = {}

    def fake_update_course(c, course_id, data):
        captured.update(course_id=course_id, data=data)

    monkeypatch.setattr("app.services.courses_service.update_course", fake_update_course)

    response = client.post("/courses/3/edit", data=VALID_COURSE_FORM_DATA, follow_redirects=False)

    assert response.status_code == 302
    assert captured["course_id"] == 3
    assert captured["data"]["course_name"] == "New AI Course"


def test_archive_course_calls_service_and_redirects(client, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "app.services.courses_service.archive_course",
        lambda c, course_id: captured.update(course_id=course_id),
    )

    response = client.post("/courses/3/archive", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"] == "/courses/"
    assert captured == {"course_id": 3}
