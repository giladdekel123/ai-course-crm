import numpy as np
import pandas as pd
import scipy.sparse as sp

from app.constants import ACTIVE_LEAD_STATUSES
from app.extensions import get_ml_metrics, get_ml_pipeline
from app.repositories import leads_repo
from ml.features import CATEGORICAL_FEATURES, build_inference_frame, feature_names_out

HIGH_THRESHOLD = 0.66
MEDIUM_THRESHOLD = 0.33
TOP_FACTORS = 3

DISPLAY_LABELS = {
    "age": "Age",
    "occupation": "Occupation",
    "education": "Education",
    "technical_experience": "Technical Experience",
    "reason_for_interest": "Reason for Interest",
    "source": "Source",
    "delivery_format": "Course Format",
}


def priority_for(probability: float) -> str:
    if probability >= HIGH_THRESHOLD:
        return "High"
    if probability >= MEDIUM_THRESHOLD:
        return "Medium"
    return "Low"


def _parse_feature_name(name: str) -> str:
    if name.startswith("numeric__"):
        column = name[len("numeric__"):]
        return DISPLAY_LABELS.get(column, column)

    rest = name[len("categorical__"):]
    for column in sorted(CATEGORICAL_FEATURES, key=len, reverse=True):
        prefix = f"{column}_"
        if rest.startswith(prefix):
            category = rest[len(prefix):]
            label = DISPLAY_LABELS.get(column, column)
            return f"{label}: {category}"
    return rest


def _top_factors(contributions_row: np.ndarray, feature_names: list[str]) -> list[dict]:
    order = np.argsort(-np.abs(contributions_row))[:TOP_FACTORS]
    factors = []
    for idx in order:
        contribution = contributions_row[idx]
        if contribution == 0:
            continue
        factors.append({
            "label": _parse_feature_name(feature_names[idx]),
            "direction": "positive" if contribution > 0 else "negative",
        })
    return factors


def predict_for_active_leads(client) -> list[dict]:
    leads = leads_repo.list_active_with_course(client, ACTIVE_LEAD_STATUSES)
    if not leads:
        return []

    df = pd.DataFrame(leads)
    df["delivery_format"] = df["courses"].apply(lambda c: c["delivery_format"] if c else None)
    df["course_name"] = df["courses"].apply(lambda c: c["course_name"] if c else None)

    pipeline = get_ml_pipeline()
    X = build_inference_frame(df)
    probabilities = pipeline.predict_proba(X)[:, 1]

    preprocessor = pipeline.named_steps["preprocess"]
    classifier = pipeline.named_steps["classifier"]
    transformed = preprocessor.transform(X)
    if sp.issparse(transformed):
        transformed = transformed.toarray()
    contributions = transformed * classifier.coef_[0]
    feature_names = feature_names_out(pipeline)

    results = []
    for i, (_, row) in enumerate(df.iterrows()):
        probability = float(probabilities[i])
        results.append({
            "lead_id": row["id"],
            "name": row["name"],
            "course_name": row["course_name"],
            "status": row["status"],
            "probability": round(probability * 100, 1),
            "priority": priority_for(probability),
            "top_factors": _top_factors(contributions[i], feature_names),
        })

    results.sort(key=lambda r: -r["probability"])
    return results


def get_model_metrics() -> dict:
    return get_ml_metrics()


def summarize(predictions: list[dict]) -> dict:
    if not predictions:
        return {"total": 0, "high_count": 0, "avg_probability": 0.0}
    high_count = sum(1 for p in predictions if p["priority"] == "High")
    avg_probability = sum(p["probability"] for p in predictions) / len(predictions)
    return {
        "total": len(predictions),
        "high_count": high_count,
        "avg_probability": round(avg_probability, 1),
    }
