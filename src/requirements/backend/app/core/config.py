import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # JWT 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30분
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7일
    
    # 데이터베이스 설정
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
