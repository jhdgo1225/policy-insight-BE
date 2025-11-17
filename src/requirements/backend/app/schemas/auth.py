from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr = Field(..., description="회원의 이메일 주소")
    password: str = Field(..., min_length=10, max_length=20, description="비밀번호 (10-20자, 영대문자/영소문자/숫자/특수문자 각 1개 이상)")


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


class SignupRequest(BaseModel):
    """회원가입 요청 스키마"""
    email: EmailStr = Field(..., description="회원의 이메일 주소")
    password: str = Field(..., min_length=10, max_length=20, description="비밀번호 (10-20자, 영대문자/영소문자/숫자/특수문자 각 1개 이상)")
    name: str = Field(..., min_length=1, max_length=50, description="회원의 실명")
    phone: str = Field(..., description="회원 전화번호")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """전화번호 형식 검증 (숫자만, 11자리)"""
        if not v:
            raise ValueError("전화번호는 필수입니다")
        # 하이픈 제거
        phone_digits = re.sub(r'[-\s]', '', v)
        if not phone_digits.isdigit():
            raise ValueError("전화번호는 숫자만 입력 가능합니다")
        if len(phone_digits) != 11:
            raise ValueError("전화번호는 11자리여야 합니다")
        return phone_digits


class SignupResponse(BaseModel):
    """회원가입 응답 스키마"""
    message: str = Field(..., description="성공 메시지")


class RefreshTokenRequest(BaseModel):
    """리프레시 토큰 요청 스키마"""
    refreshToken: str = Field(..., description="리프레시 토큰")


class RefreshTokenResponse(BaseModel):
    """리프레시 토큰 응답 스키마"""
    accessToken: str = Field(..., description="새로 발급된 액세스 토큰")


class ResetPasswordNoLoginRequest(BaseModel):
    """비로그인 상태 비밀번호 변경 요청 스키마"""
    id: EmailStr = Field(..., description="회원의 이메일 주소 (ID)")
    password: str = Field(..., min_length=10, max_length=20, description="새 비밀번호 (10-20자, 영대문자/영소문자/숫자/특수문자 각 1개 이상)")


class ResetPasswordLoginRequest(BaseModel):
    """로그인 상태 비밀번호 변경 요청 스키마"""
    password: str = Field(..., min_length=10, max_length=20, description="새 비밀번호 (10-20자, 영대문자/영소문자/숫자/특수문자 각 1개 이상)")


class PasswordChangeResponse(BaseModel):
    """비밀번호 변경 응답 스키마"""
    message: str = Field(..., description="성공 메시지")


class PasswordHistoryItem(BaseModel):
    """비밀번호 변경 이력 항목 스키마"""
    title: str = Field(..., description="변경 제목")
    date: str = Field(..., description="변경 일시")


class FindIdRequest(BaseModel):
    """아이디 찾기 요청 스키마"""
    email: EmailStr = Field(..., description="회원의 이메일 주소")


class FindIdResponse(BaseModel):
    """아이디 찾기 응답 스키마"""
    id: str = Field(..., description="회원의 이메일 주소 (ID)")


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    error: str = Field(..., description="에러 메시지")


class CsrfTokenResponse(BaseModel):
    """CSRF 토큰 응답 스키마"""
    csrfToken: str = Field(..., description="CSRF 토큰")
