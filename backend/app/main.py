from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.routers import auth, leads, public

from app.dependencies import get_current_user, require_admin
from app.models import User

app = FastAPI(title="Lead Platform API")

app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(public.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"db_status": "ok", "result": result.scalar()}
