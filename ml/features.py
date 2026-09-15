"""Shared feature engineering for training and inference.

`status` is deliberately excluded from the model's feature set: for historical
(training) leads, status is terminal (Converted / Not Interested) and *is*
the label, so including it as a feature would leak the target and produce
artificially perfect metrics. Active leads scored on the ML Predictions
screen only ever carry a non-terminal status, a value the historical
training data never contains either - so it wouldn't carry real signal at
inference even if leakage weren't a concern. Status is still shown alongside
each prediction in the UI, just not fed to the model.

"Course Interest" is represented by the interested course's `delivery_format`
rather than the specific course, since the course identity itself carries no
independent signal in this dataset beyond its delivery format.
"""
from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = ["age"]
CATEGORICAL_FEATURES = [
    "occupation",
    "education",
    "technical_experience",
    "reason_for_interest",
    "source",
    "delivery_format",
]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

TERMINAL_STATUS_LABELS = {"Converted": 1, "Not Interested": 0}


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline([
        ("preprocess", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000)),
    ])


def build_training_frame(leads: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """`leads` must be joined with courses (a `delivery_format` column) and
    contain only rows with a terminal status."""
    terminal = leads[leads["status"].isin(TERMINAL_STATUS_LABELS)].copy()
    X = terminal[FEATURE_COLUMNS]
    y = terminal["status"].map(TERMINAL_STATUS_LABELS)
    return X, y


def build_inference_frame(leads: pd.DataFrame) -> pd.DataFrame:
    return leads[FEATURE_COLUMNS]


def feature_names_out(pipeline: Pipeline) -> list[str]:
    return list(pipeline.named_steps["preprocess"].get_feature_names_out())
