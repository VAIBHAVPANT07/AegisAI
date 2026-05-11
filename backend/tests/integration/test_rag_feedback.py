import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_current_user
from app.models import User
from app.models.user import SubscriptionTier

def _get_test_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    return _override_get_db

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _get_test_db()

    # override auth to return a user; default non-admin
    def _fake_user():
        u = User()
        u.id = 1
        u.email = "tester@example.com"
        u.subscription_tier = SubscriptionTier.FREE
        return u

    app.dependency_overrides[get_current_user] = _fake_user

    with TestClient(app) as c:
        yield c

def test_rag_feedback_thumbs_up(client):
    resp = client.post("/api/v1/rag/feedback", json={
        "question": "What is AI Act?",
        "answer": "It is a regulation.",
        "rating": 1
    })
    assert resp.status_code == 204

def test_rag_feedback_invalid_rating(client):
    resp = client.post("/api/v1/rag/feedback", json={
        "question": "What is AI Act?",
        "answer": "It is a regulation.",
        "rating": 0
    })
    assert resp.status_code == 422

def test_rag_feedback_thumbs_down(client):
    resp = client.post("/api/v1/rag/feedback", json={
        "question": "What is GDPR?",
        "answer": "Data protection.",
        "rating": -1
    })
    assert resp.status_code == 204
