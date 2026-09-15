from app.services import courses_service


def test_list_courses_computes_enrolled_interested_and_capacity_pct(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.courses_repo.list_all",
        lambda client, active_only=False: [
            {"id": 1, "course_name": "AI Foundations", "capacity": 50},
            {"id": 2, "course_name": "Zero Capacity Course", "capacity": 0},
        ],
    )
    monkeypatch.setattr(
        "app.repositories.courses_repo.enrolled_counts_by_course",
        lambda client: {1: 25},
    )
    monkeypatch.setattr(
        "app.repositories.courses_repo.interested_counts_by_course",
        lambda client, active_statuses: {1: 10},
    )

    courses = courses_service.list_courses(object())

    assert courses[0]["enrolled_count"] == 25
    assert courses[0]["interested_count"] == 10
    assert courses[0]["capacity_filled_pct"] == 50.0

    # A course with no capacity must not raise a ZeroDivisionError.
    assert courses[1]["enrolled_count"] == 0
    assert courses[1]["capacity_filled_pct"] == 0.0


def test_get_course_passes_through(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.courses_repo.get_by_id",
        lambda client, course_id: {"id": course_id, "course_name": "AI Foundations"},
    )

    assert courses_service.get_course(object(), 1)["course_name"] == "AI Foundations"


def test_create_course_passes_through(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.courses_repo.create",
        lambda client, data: {"id": 1, **data},
    )

    course = courses_service.create_course(object(), {"course_name": "New Course"})

    assert course["id"] == 1
    assert course["course_name"] == "New Course"


def test_update_course_passes_through(monkeypatch):
    captured = {}

    def fake_update(client, course_id, data):
        captured.update(course_id=course_id, data=data)
        return {"id": course_id, **data}

    monkeypatch.setattr("app.repositories.courses_repo.update", fake_update)

    courses_service.update_course(object(), 3, {"price": 500})

    assert captured == {"course_id": 3, "data": {"price": 500}}


def test_archive_course_sets_is_active_false(monkeypatch):
    captured = {}

    def fake_archive(client, course_id):
        captured["course_id"] = course_id
        return {"id": course_id, "is_active": False}

    monkeypatch.setattr("app.repositories.courses_repo.archive", fake_archive)

    result = courses_service.archive_course(object(), 9)

    assert captured["course_id"] == 9
    assert result["is_active"] is False
