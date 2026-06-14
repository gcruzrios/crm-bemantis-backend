from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from app.core.enums import QuoteStatus
from app.schemas.quote_item import QuoteItemCreate, QuoteItemRead


class QuoteCreate(BaseModel):
    deal_id: str
    valid_until: Optional[date] = None
    tax_rate: Decimal = Decimal("13.0")
    currency: str = "USD"
    notes: Optional[str] = None
    items: List[QuoteItemCreate]


class QuoteUpdate(BaseModel):
    valid_until: Optional[date] = None
    tax_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[QuoteItemCreate]] = None


class QuoteStatusUpdate(BaseModel):
    status: QuoteStatus


class QuoteRead(BaseModel):
    id: str
    deal_id: str
    quote_number: Optional[str]
    status: QuoteStatus
    valid_until: Optional[date]
    subtotal: Decimal
    tax_rate: Decimal
    total: Decimal
    currency: str
    notes: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]
    items: List[QuoteItemRead] = []

    model_config = {"from_attributes": True}
