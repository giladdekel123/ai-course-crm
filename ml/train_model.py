"""Train the lead purchase-propensity model from Supabase data.

Usage (from the project root, with the venv active):
    python -m ml.train_model

Pulls every historical lead with a terminal status (Converted / Not
Interested) from Supabase, joined with its interested course's
delivery_format, trains a logistic regression pipeline, and writes:
  - ml/model.joblib   the fitted pipeline
  - ml/metrics.json   accuracy/precision/recall/F1/ROC-AUC computed on a
                       held-out test split - real numbers, not placeholders.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from supabase import create_client

from ml.features import build_pipeline, build_training_frame

ML_DIR = Path(__file__).resolve().parent
MODEL_PATH = ML_DIR / "model.joblib"
METRICS_PATH = ML_DIR / "metrics.json"

TEST_SIZE = 0.2
RANDOM_STATE = 42


def load_historical_leads(client) -> pd.DataFrame:
    response = (
        client.table("leads")
        .select("age,occupation,education,technical_experience,reason_for_interest,"
                "source,status,courses(delivery_format)")
        .in_("status", ["Converted", "Not Interested"])
        .execute()
    )
    rows = response.data
    df = pd.DataFrame(rows)
    df["delivery_format"] = df["courses"].apply(lambda c: c["delivery_format"] if c else None)
    df = df.drop(columns=["courses"])
    return df


def evaluate(pipeline, X_test, y_test) -> dict:
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }


def main():
    load_dotenv()
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    leads = load_historical_leads(client)
    X, y = build_training_frame(leads)
    print(f"Training on {len(X)} historical leads "
          f"({int(y.sum())} Converted, {int((1 - y).sum())} Not Interested)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    metrics = evaluate(pipeline, X_test, y_test)
    metrics.update({
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_total": len(X),
        "converted_rate": float(y.mean()),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    })

    joblib.dump(pipeline, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))

    print("Metrics (on held-out test split):")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    main()
