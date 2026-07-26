from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.routers import auth

from app.dependencies import get_current_user, require_admin
from app.models import User

app = FastAPI(title="Lead Platform API")

app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"db_status": "ok", "result": result.scalar()}

@app.get("/auth/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {"id": str(current_user.id), "email": current_user.email, "role": current_user.role}


@app.get("/auth/admin-only")
def admin_only(current_user: User = Depends(require_admin)):
    return {"message": f"Hello admin {current_user.email}"}