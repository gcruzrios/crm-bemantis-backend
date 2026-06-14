from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.core.enums import ActivityType


class ActivityCreate(BaseModel):
    deal_id: Optional[str] = None
    contact_id: Optional[str] = None
    type: ActivityType
    subject: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class ActivityUpdate(BaseModel):
    type: Optional[ActivityType] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class ActivityRead(BaseModel):
    id: str
    deal_id: Optional[str]
    contact_id: Optional[str]
    owner_id: str
    type: ActivityType
    subject: str
    description: Optional[str]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
