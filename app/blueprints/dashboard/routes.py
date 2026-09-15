from flask import Blueprint, render_template

from app.extensions import get_supabase_client
from app.services import dashboard_service

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    client = get_supabase_client()
    stats = dashboard_service.get_dashboard_stats(client)
    return render_template("dashboard/index.html", stats=stats)
