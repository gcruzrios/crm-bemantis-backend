from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    default_price: Optional[Decimal] = None
    unit: str = "proyecto"
    is_active: bool = True


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_price: Optional[Decimal] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceRead(BaseModel):
    id: str
    name: str
    description: Optional[str]
    default_price: Optional[Decimal]
    unit: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}
