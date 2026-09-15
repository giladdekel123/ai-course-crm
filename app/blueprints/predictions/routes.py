from flask import Blueprint, render_template

from app.extensions import get_supabase_client
from app.services import ml_service

bp = Blueprint("predictions", __name__, url_prefix="/predictions")


@bp.route("/")
def list_predictions():
    client = get_supabase_client()
    predictions = ml_service.predict_for_active_leads(client)
    metrics = ml_service.get_model_metrics()
    summary = ml_service.summarize(predictions)
    return render_template(
        "predictions/list.html", predictions=predictions, metrics=metrics, summary=summary,
    )
