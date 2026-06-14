from uuid import uuid4
from sqlalchemy import String, Text, Integer, Date, Numeric, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.core.enums import DealStage


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False)
    contact_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("contacts.id", ondelete="SET NULL"))
    owner_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    stage: Mapped[str] = mapped_column(
        Enum(DealStage, name="deal_stage", create_type=False),
        nullable=False,
        default=DealStage.prospecto,
    )
    estimated_value: Mapped[float | None] = mapped_column(Numeric(12, 2))
    probability: Mapped[int | None] = mapped_column(Integer)
    expected_close_date = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="deals")
    owner: Mapped["User"] = relationship("User", back_populates="deals")
    quotes: Mapped[list["Quote"]] = relationship("Quote", back_populates="deal", cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="deal")
