from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ContactCreate(BaseModel):
    company_id: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_primary: bool = False


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_primary: Optional[bool] = None


class ContactRead(BaseModel):
    id: str
    company_id: str
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    role: Optional[str]
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}
