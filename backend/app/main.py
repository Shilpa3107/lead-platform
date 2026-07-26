from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.routers import auth, leads, public, users

from app.dependencies import get_current_user, require_admin
from app.models import User

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Lead Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "lead-platform-iota.vercel.app",  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(public.router)
app.include_router(users.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"db_status": "ok", "result": result.scalar()}
