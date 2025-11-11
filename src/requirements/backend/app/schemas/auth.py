from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr = Field(..., description="회원의 이메일 주소")
    password: str = Field(..., description="비밀번호")


class LoginResponse(BaseModel):
    """로그인 응답 스키마"""
    id: int = Field(..., description="회원 고유 식별번호")
    accessToken: str = Field(..., description="액세스 토큰")
    refreshToken: str = Field(..., description="리프레시 토큰")
    email: str = Field(..., description="회원의 이메일 주소")
    name: str = Field(..., description="회원의 실명")
    image: str = Field(..., description="프로필 이미지 경로")
    phone: str = Field(..., description="회원 전화번호")
    
    class Config:
        from_attributes = True


class LogoutResponse(BaseModel):
    """로그아웃 응답 스키마"""
    message: str = Field(..., description="성공 메시지")


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    error: str = Field(..., description="에러 메시지")
