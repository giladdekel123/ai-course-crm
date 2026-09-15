from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.blueprints.courses.forms import CourseForm
from app.extensions import get_supabase_client
from app.services import courses_service

bp = Blueprint("courses", __name__, url_prefix="/courses")


@bp.route("/")
def list_courses():
    client = get_supabase_client()
    courses = courses_service.list_courses(client, active_only=False)
    return render_template("courses/list.html", courses=courses)


@bp.route("/new", methods=["GET", "POST"])
def new_course():
    form = CourseForm()
    if form.validate_on_submit():
        client = get_supabase_client()
        data = {
            "course_name": form.course_name.data,
            "description": form.description.data,
            "start_date": form.start_date.data.isoformat(),
            "duration": form.duration.data,
            "price": float(form.price.data),
            "capacity": form.capacity.data,
            "delivery_format": form.delivery_format.data,
        }
        course = courses_service.create_course(client, data)
        flash(f"Course '{course['course_name']}' created.", "success")
        return redirect(url_for("courses.list_courses"))

    return render_template("courses/form.html", form=form, mode="new")


@bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
def edit_course(course_id):
    client = get_supabase_client()
    course = courses_service.get_course(client, course_id)
    if course is None:
        abort(404)

    if request.method == "GET":
        form = CourseForm(data={**course, "start_date": date.fromisoformat(course["start_date"])})
    else:
        form = CourseForm()

    if form.validate_on_submit():
        data = {
            "course_name": form.course_name.data,
            "description": form.description.data,
            "start_date": form.start_date.data.isoformat(),
            "duration": form.duration.data,
            "price": float(form.price.data),
            "capacity": form.capacity.data,
            "delivery_format": form.delivery_format.data,
        }
        courses_service.update_course(client, course_id, data)
        flash("Course updated.", "success")
        return redirect(url_for("courses.list_courses"))

    return render_template("courses/form.html", form=form, mode="edit", course=course)


@bp.route("/<int:course_id>/archive", methods=["POST"])
def archive_course(course_id):
    client = get_supabase_client()
    courses_service.archive_course(client, course_id)
    flash("Course archived.", "success")
    return redirect(url_for("courses.list_courses"))
