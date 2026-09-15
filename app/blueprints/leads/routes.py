from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.blueprints.leads.forms import ConvertForm, LeadForm, StatusForm
from app.constants import LEAD_STATUSES, SOURCES
from app.extensions import get_supabase_client
from app.services import courses_service, leads_service

bp = Blueprint("leads", __name__, url_prefix="/leads")


@bp.route("/")
def list_leads():
    client = get_supabase_client()
    status = request.args.get("status") or None
    source = request.args.get("source") or None
    search = request.args.get("q") or None
    leads = leads_service.list_leads(client, status=status, source=source, search=search)
    return render_template(
        "leads/list.html",
        leads=leads,
        statuses=LEAD_STATUSES,
        sources=SOURCES,
        selected_status=status,
        selected_source=source,
        search=search or "",
    )


@bp.route("/new", methods=["GET", "POST"])
def new_lead():
    client = get_supabase_client()
    courses = courses_service.list_courses(client, active_only=True)
    form = LeadForm()
    form.course_interest_id.choices = [(c["id"], c["course_name"]) for c in courses]

    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "phone": form.phone.data,
            "email": form.email.data,
            "age": form.age.data,
            "city": form.city.data,
            "occupation": form.occupation.data,
            "education": form.education.data,
            "technical_experience": form.technical_experience.data,
            "reason_for_interest": form.reason_for_interest.data,
            "source": form.source.data,
            "course_interest_id": form.course_interest_id.data,
        }
        lead = leads_service.create_lead(client, data)
        flash(f"Lead '{lead['name']}' created.", "success")
        return redirect(url_for("leads.view_lead", lead_id=lead["id"]))

    return render_template("leads/form.html", form=form, mode="new")


@bp.route("/<int:lead_id>")
def view_lead(lead_id):
    client = get_supabase_client()
    lead = leads_service.get_lead(client, lead_id)
    if lead is None:
        abort(404)
    courses = courses_service.list_courses(client, active_only=True)

    status_form = StatusForm(status=lead["status"])
    convert_form = ConvertForm(course_id=lead.get("course_interest_id"))
    convert_form.course_id.choices = [(c["id"], c["course_name"]) for c in courses]

    return render_template(
        "leads/detail.html",
        lead=lead,
        status_form=status_form,
        convert_form=convert_form,
    )


@bp.route("/<int:lead_id>/edit", methods=["GET", "POST"])
def edit_lead(lead_id):
    client = get_supabase_client()
    lead = leads_service.get_lead(client, lead_id)
    if lead is None:
        abort(404)
    courses = courses_service.list_courses(client, active_only=True)

    form = LeadForm(data=lead) if request.method == "GET" else LeadForm()
    form.course_interest_id.choices = [(c["id"], c["course_name"]) for c in courses]

    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "phone": form.phone.data,
            "email": form.email.data,
            "age": form.age.data,
            "city": form.city.data,
            "occupation": form.occupation.data,
            "education": form.education.data,
            "technical_experience": form.technical_experience.data,
            "reason_for_interest": form.reason_for_interest.data,
            "source": form.source.data,
            "course_interest_id": form.course_interest_id.data,
        }
        leads_service.update_lead(client, lead_id, data)
        flash("Lead updated.", "success")
        return redirect(url_for("leads.view_lead", lead_id=lead_id))

    return render_template("leads/form.html", form=form, mode="edit", lead=lead)


@bp.route("/<int:lead_id>/status", methods=["POST"])
def update_status(lead_id):
    client = get_supabase_client()
    form = StatusForm()
    if form.validate_on_submit():
        leads_service.change_status(client, lead_id, form.status.data)
        flash(f"Status updated to {form.status.data}.", "success")
    return redirect(url_for("leads.view_lead", lead_id=lead_id))


@bp.route("/<int:lead_id>/convert", methods=["POST"])
def convert_lead(lead_id):
    client = get_supabase_client()
    courses = courses_service.list_courses(client, active_only=True)
    form = ConvertForm()
    form.course_id.choices = [(c["id"], c["course_name"]) for c in courses]

    if form.validate_on_submit():
        leads_service.convert_lead(
            client,
            lead_id,
            form.course_id.data,
            form.enrollment_date.data.isoformat(),
            float(form.amount_paid.data),
            form.payment_method.data,
        )
        flash("Lead converted to a paid registration.", "success")
    else:
        flash("Could not convert lead - please check the form.", "error")
    return redirect(url_for("leads.view_lead", lead_id=lead_id))
