import uuid
from pydantic import BaseModel, EmailStr
from app.models import UserRole, LeadStatus
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.member


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    role: UserRole

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = None


class LeadUpdate(BaseModel):
    status: Optional[LeadStatus] = None
    assigned_to_id: Optional[uuid.UUID] = None


class LeadOut(BaseModel):
    id: uuid.UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    source: Optional[str]
    status: LeadStatus
    assigned_to_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteCreate(BaseModel):
    content: str


class NoteOut(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityLogOut(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    actor_id: Optional[uuid.UUID]
    action: str
    details: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedLeads(BaseModel):
    items: List[LeadOut]
    total: int
    page: int
    page_size: int