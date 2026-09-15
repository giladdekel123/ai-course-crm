import pandas as pd

from ml.features import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    build_inference_frame,
    build_pipeline,
    build_training_frame,
    feature_names_out,
)

LEADS = pd.DataFrame([
    {"age": 25, "occupation": "Student", "education": "Bachelor's", "technical_experience": "Beginner",
     "reason_for_interest": "Career change", "source": "Referral", "delivery_format": "Online", "status": "Converted"},
    {"age": 40, "occupation": "Software Engineer", "education": "Master's", "technical_experience": "Advanced",
     "reason_for_interest": "Employer requirement", "source": "Website", "delivery_format": "Hybrid", "status": "Converted"},
    {"age": 30, "occupation": "Teacher", "education": "PhD", "technical_experience": "None",
     "reason_for_interest": "General curiosity", "source": "Cold Outreach", "delivery_format": "In-person", "status": "Not Interested"},
    {"age": 35, "occupation": "Unemployed", "education": "High School", "technical_experience": "Beginner",
     "reason_for_interest": "Academic interest", "source": "Advertisement", "delivery_format": "Online", "status": "Not Interested"},
    {"age": 28, "occupation": "Data Analyst", "education": "Bachelor's", "technical_experience": "Intermediate",
     "reason_for_interest": "Skill upgrade", "source": "Event", "delivery_format": "Hybrid", "status": "Interested"},
    {"age": 33, "occupation": "Business Owner", "education": "Master's", "technical_experience": "Advanced",
     "reason_for_interest": "Starting a business", "source": "Partner Organization", "delivery_format": "Online", "status": "New"},
])


def test_status_is_never_a_model_feature():
    # Deliberate: status is terminal for training rows and would leak the label.
    assert "status" not in FEATURE_COLUMNS
    assert "status" not in NUMERIC_FEATURES
    assert "status" not in CATEGORICAL_FEATURES


def test_build_training_frame_keeps_only_terminal_statuses_and_maps_labels():
    X, y = build_training_frame(LEADS)

    assert len(X) == 4  # excludes the "Interested" and "New" (non-terminal) rows
    assert set(y.unique()) == {0, 1}
    assert list(X.columns) == FEATURE_COLUMNS
    # Terminal rows keep their original order: Converted, Converted, Not Interested, Not Interested.
    assert list(y) == [1, 1, 0, 0]


def test_build_inference_frame_selects_only_feature_columns():
    X = build_inference_frame(LEADS)

    assert list(X.columns) == FEATURE_COLUMNS
    assert len(X) == len(LEADS)


def test_pipeline_fits_and_predicts_probabilities_in_range():
    X, y = build_training_frame(LEADS)
    pipeline = build_pipeline()
    pipeline.fit(X, y)

    probabilities = pipeline.predict_proba(build_inference_frame(LEADS))[:, 1]

    assert len(probabilities) == len(LEADS)
    assert all(0.0 <= p <= 1.0 for p in probabilities)


def test_pipeline_handles_unseen_categories_at_inference():
    X, y = build_training_frame(LEADS)
    pipeline = build_pipeline()
    pipeline.fit(X, y)

    unseen = pd.DataFrame([{
        "age": 50, "occupation": "Healthcare Professional", "education": "Other",
        "technical_experience": "Intermediate", "reason_for_interest": "Career change",
        "source": "Social Media", "delivery_format": "Hybrid",
    }])

    # None of these exact category combinations were in the training fixture;
    # OneHotEncoder(handle_unknown="ignore") must not raise.
    probability = pipeline.predict_proba(unseen)[0, 1]
    assert 0.0 <= probability <= 1.0


def test_feature_names_out_are_prefixed_by_transformer():
    X, y = build_training_frame(LEADS)
    pipeline = build_pipeline()
    pipeline.fit(X, y)

    names = feature_names_out(pipeline)

    assert any(name.startswith("numeric__age") for name in names)
    assert any(name.startswith("categorical__") for name in names)
