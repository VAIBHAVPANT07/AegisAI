import pytest
from app.models.notification import Notification
from app.models.user import User


def test_notification_model_exists():
    assert Notification.__tablename__ == "notifications"


def test_user_has_notifications_relationship():
    assert hasattr(User, "notifications")


def test_notification_defaults():
    n = Notification(
        user_id=1,
        notification_type="alert",
        title="Test Title",
        message="Test message body"
    )
    assert n.is_read == False
    assert n.resource_type is None
    assert n.resource_id is None


def test_notification_required_fields():
    """Notification should hold all required fields correctly."""
    n = Notification(
        user_id=42,
        notification_type="warning",
        title="Warning Title",
        message="Something needs attention"
    )
    assert n.user_id == 42
    assert n.notification_type == "warning"
    assert n.title == "Warning Title"
    assert n.message == "Something needs attention"
