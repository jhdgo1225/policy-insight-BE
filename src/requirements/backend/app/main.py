from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db.base import get_db, Base, engine
from .models import user as models
from .schemas import user as schemas

# Create database tables
Base.metadata.create_all(bind=engine)
from .routers import health
from .routers import tasks

app = FastAPI(
    title="Policy Insight API",
    description="Policy Insight Backend API with Celery 태스크 관리",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(tasks.router)

@app.get("/")
async def root():
    return {
        "message": "Policy Insight API 서버가 실행 중입니다.",
        "docs_url": "/docs",
        "tasks_api": "/tasks"
    }

