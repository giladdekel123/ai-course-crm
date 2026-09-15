import pytest

from app import create_app
from app.config import Config


class TestConfig(Config):
    SECRET_KEY = "test-secret"
    WTF_CSRF_ENABLED = False
    SUPABASE_URL = "https://example.supabase.co"
    SUPABASE_SERVICE_KEY = "test-key"


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def fake_supabase_client(monkeypatch):
    """Stand in for the real Supabase client everywhere a route would build one.

    Route tests monkeypatch the service layer, so the client value itself is
    never used - this just stops routes from trying to construct a real
    supabase-py client (and validate real credentials) during tests.
    """
    sentinel = object()
    for module in (
        "app.blueprints.dashboard.routes",
        "app.blueprints.leads.routes",
        "app.blueprints.courses.routes",
        "app.blueprints.predictions.routes",
    ):
        monkeypatch.setattr(f"{module}.get_supabase_client", lambda: sentinel)
    return sentinel
