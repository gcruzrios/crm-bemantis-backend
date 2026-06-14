from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from app.core.enums import DealStage


class DealCreate(BaseModel):
    company_id: str
    contact_id: Optional[str] = None
    title: str
    stage: DealStage = DealStage.prospecto
    estimated_value: Optional[Decimal] = None
    probability: Optional[int] = None
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None


class DealUpdate(BaseModel):
    contact_id: Optional[str] = None
    title: Optional[str] = None
    stage: Optional[DealStage] = None
    estimated_value: Optional[Decimal] = None
    probability: Optional[int] = None
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None


class DealStageUpdate(BaseModel):
    stage: DealStage


class DealRead(BaseModel):
    id: str
    company_id: str
    contact_id: Optional[str]
    owner_id: str
    title: str
    stage: DealStage
    estimated_value: Optional[Decimal]
    probability: Optional[int]
    expected_close_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
