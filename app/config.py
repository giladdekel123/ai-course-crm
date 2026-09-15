import os


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev")
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
    ML_MODEL_PATH = os.environ.get("ML_MODEL_PATH", "ml/model.joblib")
    ML_METRICS_PATH = os.environ.get("ML_METRICS_PATH", "ml/metrics.json")
