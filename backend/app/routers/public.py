from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Lead
from app.schemas import LeadCreate, LeadOut
from app.routers.leads import log_activity

router = APIRouter(prefix="/public", tags=["public"])


@router.post("/leads", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def capture_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(**payload.model_dump())  # status defaults to "new", assigned_to_id stays null — schema doesn't expose those fields
    db.add(lead)
    db.flush()
    log_activity(db, lead.id, actor_id=None, action="created", details="Submitted via public capture form")
    db.commit()
    db.refresh(lead)
    return lead