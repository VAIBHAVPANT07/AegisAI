"""
Notification model — stores in-app events for users.
Copyright (C) 2024 Sarthak Doshi (github.com/SdSarthak)
SPDX-License-Identifier: AGPL-3.0-only

TODO for contributors (good first issue):
  - This model is complete. Register it in app/models/__init__.py and
    create an Alembic migration so the table is created.
  - Acceptance criteria: `alembic revision --autogenerate` produces a
    migration that creates the `notifications` table.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import sqlalchemy as sa
import enum
from app.core.database import Base


class NotificationType(str, enum.Enum):
    SYSTEM_CLASSIFIED = "system_classified"
    DOCUMENT_GENERATED = "document_generated"
    GUARD_BLOCK = "guard_block"
    COMPLIANCE_DRIFT = "compliance_drift"
    REASSESSMENT_DUE = "reassessment_due"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    notification_type = Column(String(100), nullable=False, index=True)  # NotificationType value
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, server_default=sa.false(), default=False, index=True)

    # Optional link back to the relevant resource
    # resource_type and resource_id form a generic (polymorphic) reference.
    # No FK is used intentionally so notifications can point to any resource type
    # (e.g. "ai_system", "document") without requiring a join table per type.
    resource_type = Column(String(100), nullable=True)  # e.g. "ai_system", "document"
    resource_id = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    # Relationships
    user = relationship("User", back_populates="notifications")
