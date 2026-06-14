from uuid import uuid4
from sqlalchemy import String, Text, Date, Numeric, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.core.enums import QuoteStatus


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    deal_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("deals.id", ondelete="RESTRICT"), nullable=False)
    quote_number: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    status: Mapped[str] = mapped_column(
        Enum(QuoteStatus, name="quote_status", create_type=False),
        nullable=False,
        default=QuoteStatus.borrador,
    )
    valid_until = mapped_column(Date)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=13.0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent_at = mapped_column(DateTime(timezone=True))

    deal: Mapped["Deal"] = relationship("Deal", back_populates="quotes")
    items: Mapped[list["QuoteItem"]] = relationship(
        "QuoteItem", back_populates="quote", cascade="all, delete-orphan"
    )
