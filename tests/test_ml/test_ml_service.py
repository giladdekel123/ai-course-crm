import pandas as pd
import pytest

from app.services import ml_service
from ml.features import build_pipeline, build_training_frame

TRAINING_LEADS = pd.DataFrame([
    {"age": 25, "occupation": "Student", "education": "Bachelor's", "technical_experience": "Beginner",
     "reason_for_interest": "Career change", "source": "Referral", "delivery_format": "Online", "status": "Converted"},
    {"age": 40, "occupation": "Software Engineer", "education": "Master's", "technical_experience": "Advanced",
     "reason_for_interest": "Employer requirement", "source": "Referral", "delivery_format": "Hybrid", "status": "Converted"},
    {"age": 45, "occupation": "Business Owner", "education": "PhD", "technical_experience": "Advanced",
     "reason_for_interest": "Employer requirement", "source": "Partner Organization", "delivery_format": "Online", "status": "Converted"},
    {"age": 30, "occupation": "Teacher", "education": "PhD", "technical_experience": "None",
     "reason_for_interest": "General curiosity", "source": "Cold Outreach", "delivery_format": "In-person", "status": "Not Interested"},
    {"age": 35, "occupation": "Unemployed", "education": "High School", "technical_experience": "Beginner",
     "reason_for_interest": "Academic interest", "source": "Advertisement", "delivery_format": "Online", "status": "Not Interested"},
    {"age": 50, "occupation": "Student", "education": "High School", "technical_experience": "None",
     "reason_for_interest": "General curiosity", "source": "Cold Outreach", "delivery_format": "In-person", "status": "Not Interested"},
])


@pytest.fixture
def fitted_pipeline():
    X, y = build_training_frame(TRAINING_LEADS)
    pipeline = build_pipeline()
    pipeline.fit(X, y)
    return pipeline


@pytest.mark.parametrize("probability,expected", [
    (0.66, "High"),
    (0.9, "High"),
    (0.659999, "Medium"),
    (0.33, "Medium"),
    (0.5, "Medium"),
    (0.329999, "Low"),
    (0.0, "Low"),
])
def test_priority_thresholds(probability, expected):
    assert ml_service.priority_for(probability) == expected


def test_parse_numeric_feature_name():
    assert ml_service._parse_feature_name("numeric__age") == "Age"


def test_parse_categorical_feature_name_with_underscored_column():
    # "technical_experience" itself contains underscores, so the prefix match
    # must not stop at the first underscore.
    label = ml_service._parse_feature_name("categorical__technical_experience_Advanced")
    assert label == "Technical Experience: Advanced"


def test_parse_categorical_feature_name_for_reason_for_interest():
    label = ml_service._parse_feature_name("categorical__reason_for_interest_Career change")
    assert label == "Reason for Interest: Career change"


def test_summarize_empty_predictions():
    assert ml_service.summarize([]) == {"total": 0, "high_count": 0, "avg_probability": 0.0}


def test_summarize_counts_high_priority_and_averages_probability():
    predictions = [
        {"priority": "High", "probability": 80.0},
        {"priority": "High", "probability": 90.0},
        {"priority": "Low", "probability": 10.0},
    ]

    summary = ml_service.summarize(predictions)

    assert summary == {"total": 3, "high_count": 2, "avg_probability": 60.0}


def test_predict_for_active_leads_returns_well_formed_predictions(monkeypatch, fitted_pipeline):
    active_leads = [
        {
            "id": 101, "name": "Priya Nair", "status": "Interested", "age": 33,
            "occupation": "Business Owner", "education": "PhD", "technical_experience": "Advanced",
            "reason_for_interest": "Employer requirement", "source": "Referral",
            "courses": {"course_name": "AI Product Management", "delivery_format": "Online"},
        },
        {
            "id": 102, "name": "Sam Lee", "status": "New", "age": 22,
            "occupation": "Student", "education": "High School", "technical_experience": "None",
            "reason_for_interest": "General curiosity", "source": "Cold Outreach",
            "courses": None,
        },
    ]
    monkeypatch.setattr(
        "app.repositories.leads_repo.list_active_with_course", lambda client, active_statuses: active_leads,
    )
    monkeypatch.setattr("app.services.ml_service.get_ml_pipeline", lambda: fitted_pipeline)

    predictions = ml_service.predict_for_active_leads(object())

    assert len(predictions) == 2
    lead_ids = {p["lead_id"] for p in predictions}
    assert lead_ids == {101, 102}

    for p in predictions:
        assert 0.0 <= p["probability"] <= 100.0
        assert p["priority"] in {"High", "Medium", "Low"}
        assert len(p["top_factors"]) <= 3
        for factor in p["top_factors"]:
            assert factor["direction"] in {"positive", "negative"}
            assert isinstance(factor["label"], str) and factor["label"]

    # Predictions should be scored/sorted highest-probability first.
    probabilities = [p["probability"] for p in predictions]
    assert probabilities == sorted(probabilities, reverse=True)

    # The lead with no course interest should surface with no course name, not a crash.
    sam = next(p for p in predictions if p["lead_id"] == 102)
    assert sam["course_name"] is None


def test_predict_for_active_leads_returns_empty_list_when_no_active_leads(monkeypatch, fitted_pipeline):
    monkeypatch.setattr(
        "app.repositories.leads_repo.list_active_with_course", lambda client, active_statuses: [],
    )
    monkeypatch.setattr("app.services.ml_service.get_ml_pipeline", lambda: fitted_pipeline)

    assert ml_service.predict_for_active_leads(object()) == []
