from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserOut
from app.dependencies import require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(User).all()