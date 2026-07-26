import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole, Lead, LeadStatus, Note, ActivityLog
from app.schemas import (
    LeadCreate, LeadUpdate, LeadOut, NoteCreate, NoteOut, UserOut,
    ActivityLogOut, PaginatedLeads,
)
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/leads", tags=["leads"])


def log_activity(db: Session, lead_id, actor_id, action: str, details: str = None):
    entry = ActivityLog(lead_id=lead_id, actor_id=actor_id, action=action, details=details)
    db.add(entry)


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(
    payload: LeadCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    lead = Lead(**payload.model_dump())
    db.add(lead)
    db.flush()  # get lead.id before commit
    log_activity(db, lead.id, current_user.id, "created", f"Lead created by {current_user.email}")
    db.commit()
    db.refresh(lead)
    return lead


@router.get("", response_model=PaginatedLeads)
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[LeadStatus] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Lead)

    # Server-side scoping: members only see their own assigned leads
    if current_user.role == UserRole.member:
        query = query.filter(Lead.assigned_to_id == current_user.id)

    if status_filter:
        query = query.filter(Lead.status == status_filter)

    total = query.count()
    items = query.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedLeads(items=items, total=total, page=page, page_size=page_size)


def get_lead_or_404_scoped(lead_id: uuid.UUID, current_user: User, db: Session) -> Lead:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    if current_user.role == UserRole.member and lead.assigned_to_id != current_user.id:
        # 404, not 403 — don't reveal that a lead exists that they're not allowed to see
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(
    lead_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_lead_or_404_scoped(lead_id, current_user, db)


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: uuid.UUID,
    payload: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = get_lead_or_404_scoped(lead_id, current_user, db)

    if payload.assigned_to_id is not None:
        if current_user.role != UserRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can assign leads")
        assignee = db.query(User).filter(User.id == payload.assigned_to_id).first()
        if assignee is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee does not exist")
        old_assignee = lead.assigned_to_id
        lead.assigned_to_id = payload.assigned_to_id
        log_activity(db, lead.id, current_user.id, "assigned", f"Reassigned from {old_assignee} to {payload.assigned_to_id}")

    if payload.status is not None:
        old_status = lead.status
        lead.status = payload.status
        log_activity(db, lead.id, current_user.id, "status_changed", f"{old_status.value} -> {payload.status.value}")

    db.commit()
    db.refresh(lead)
    return lead


@router.post("/{lead_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def add_note(
    lead_id: uuid.UUID,
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = get_lead_or_404_scoped(lead_id, current_user, db)
    note = Note(lead_id=lead.id, author_id=current_user.id, content=payload.content)
    db.add(note)
    log_activity(db, lead.id, current_user.id, "note_added", payload.content[:100])
    db.commit()
    db.refresh(note)
    return note


@router.get("/{lead_id}/activity", response_model=list[ActivityLogOut])
def get_activity(
    lead_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_lead_or_404_scoped(lead_id, current_user, db)
    return db.query(ActivityLog).filter(ActivityLog.lead_id == lead_id).order_by(ActivityLog.created_at.desc()).all()

@router.get("/../users", response_model=list[UserOut])
def list_users(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).all()