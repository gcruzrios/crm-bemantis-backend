from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class QuoteItemCreate(BaseModel):
    service_id: Optional[str] = None
    description: str
    quantity: Decimal
    unit_price: Decimal


class QuoteItemRead(BaseModel):
    id: str
    quote_id: str
    service_id: Optional[str]
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal

    model_config = {"from_attributes": True}
