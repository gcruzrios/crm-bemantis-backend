from uuid import uuid4
from sqlalchemy import Text, Numeric, ForeignKey, Computed
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base


class QuoteItem(Base):
    __tablename__ = "quote_items"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    quote_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("services.id", ondelete="SET NULL"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[float] = mapped_column(
        Numeric(12, 2), Computed("quantity * unit_price", persisted=True)
    )

    quote: Mapped["Quote"] = relationship("Quote", back_populates="items")
    service: Mapped["Service | None"] = relationship("Service")
