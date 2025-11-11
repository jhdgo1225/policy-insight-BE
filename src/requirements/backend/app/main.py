from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .db.base import get_db, Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)
from .routers import health
from .routers import auth
from .routers import user

# HTTPBearer 스키마 정의 (Swagger UI에서 "Authorize" 버튼 활성화)
security = HTTPBearer()

app = FastAPI(
    title="Policy Insight API",
    description="Policy Insight Backend API with Celery 태스크 관리",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True  # 토큰을 브라우저에 저장하여 새로고침 시에도 유지
    }
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
app.include_router(auth.router)
app.include_router(user.router)
