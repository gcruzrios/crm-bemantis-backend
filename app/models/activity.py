from uuid import uuid4
from sqlalchemy import String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.core.enums import ActivityType


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    deal_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("deals.id", ondelete="SET NULL"))
    contact_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("contacts.id", ondelete="SET NULL"))
    owner_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    type: Mapped[str] = mapped_column(
        Enum(ActivityType, name="activity_type", create_type=False), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    due_date = mapped_column(DateTime(timezone=True))
    completed_at = mapped_column(DateTime(timezone=True))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    deal: Mapped["Deal | None"] = relationship("Deal", back_populates="activities")
    owner: Mapped["User"] = relationship("User", back_populates="activities")
