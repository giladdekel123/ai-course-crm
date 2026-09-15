import json

import joblib
from flask import current_app, g
from supabase import Client, create_client


def get_supabase_client() -> Client:
    if "supabase_client" not in g:
        g.supabase_client = create_client(
            current_app.config["SUPABASE_URL"],
            current_app.config["SUPABASE_SERVICE_KEY"],
        )
    return g.supabase_client


def get_ml_pipeline():
    if "ml_pipeline" not in current_app.extensions:
        current_app.extensions["ml_pipeline"] = joblib.load(current_app.config["ML_MODEL_PATH"])
    return current_app.extensions["ml_pipeline"]


def get_ml_metrics() -> dict:
    if "ml_metrics" not in current_app.extensions:
        with open(current_app.config["ML_METRICS_PATH"], encoding="utf-8") as f:
            current_app.extensions["ml_metrics"] = json.load(f)
    return current_app.extensions["ml_metrics"]
