from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class UserInfoResponse(BaseModel):
    """사용자 정보 조회 응답 스키마"""
    id: int = Field(..., description="회원 고유 식별번호")
    email: str = Field(..., description="회원의 이메일 주소")
    name: str = Field(..., description="회원의 실명")
    image: str = Field(..., description="프로필 이미지 경로")
    phone: str = Field(..., description="회원 전화번호")
    
    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    """사용자 정보 수정 요청 스키마"""
    image: Optional[str] = Field(None, max_length=500, description="프로필 이미지 경로")
    phone: Optional[str] = Field(None, description="회원 전화번호 (숫자 11자리)")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """전화번호 형식 검증 (숫자만, 11자리)"""
        if v is None:
            return v
        # 하이픈 제거
        phone_digits = re.sub(r'[-\s]', '', v)
        if not phone_digits.isdigit():
            raise ValueError("전화번호는 숫자만 입력 가능합니다")
        if len(phone_digits) != 11:
            raise ValueError("전화번호는 11자리여야 합니다")
        return phone_digits


class UpdateUserResponse(BaseModel):
    """사용자 정보 수정 응답 스키마"""
    image: str = Field(..., description="프로필 이미지 경로")
    phone: str = Field(..., description="회원 전화번호")


class DeleteUserResponse(BaseModel):
    """회원 탈퇴 응답 스키마"""
    message: str = Field(..., description="성공 메시지")


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    error: str = Field(..., description="에러 메시지")
