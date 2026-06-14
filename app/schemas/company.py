from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
from app.core.enums import CompanySource


class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    source: Optional[CompanySource] = None
    notes: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    source: Optional[CompanySource] = None
    notes: Optional[str] = None


class CompanyRead(BaseModel):
    id: str
    name: str
    industry: Optional[str]
    website: Optional[str]
    country: Optional[str]
    city: Optional[str]
    source: Optional[CompanySource]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
