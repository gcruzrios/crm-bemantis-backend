from uuid import uuid4
from sqlalchemy import String, Text, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    default_price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    unit: Mapped[str | None] = mapped_column(String(50), default="proyecto")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
