from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.user import (
    UserInfoResponse, UpdateUserRequest, 
    UpdateUserResponse, DeleteUserResponse,
    ErrorResponse
)
from app.services import user as user_service

router = APIRouter(prefix="/api/v1/user", tags=["user"])

@router.get(
    '/me',
    response_model=UserInfoResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def read_user_info(
    authorization: str = Header(..., description="Bearer {access_token}"),
    db: Session = Depends(get_db)
):
    """
    내 정보 조회 API
    
    액세스 토큰을 검증하고 사용자 정보를 조회합니다.
    
    - **Authorization Header**: Bearer {access_token} 형식
    
    Returns:
        UserInfoResponse: 사용자 정보 (id, email, name, image, phone)
    """
    try:
        return user_service.get_user_info(db, authorization)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )

@router.put(
    '/me',
    response_model=UpdateUserResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def update_user_info(
    update_data: UpdateUserRequest,
    authorization: str = Header(..., description="Bearer {access_token}"),
    db: Session = Depends(get_db)
):
    """
    내 정보 수정 API
    
    액세스 토큰을 검증하고 사용자 정보를 수정합니다.
    
    - **Authorization Header**: Bearer {access_token} 형식
    - **image**: 프로필 이미지 경로 (선택)
    - **phone**: 전화번호 (숫자 11자리, 선택)
    
    Returns:
        UpdateUserResponse: 수정된 사용자 정보 (image, phone)
    """
    try:
        return user_service.update_user_info(db, update_data, authorization)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )

@router.delete(
    '/me',
    response_model=DeleteUserResponse,
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def delete_user_info(
    authorization: str = Header(..., description="Bearer {access_token}"),
    db: Session = Depends(get_db)
):
    """
    회원 탈퇴 API
    
    액세스 토큰을 검증하고 회원 탈퇴를 처리합니다.
    계정 상태를 'W'(탈퇴)로 변경하고 탈퇴 일시를 기록합니다.
    
    - **Authorization Header**: Bearer {access_token} 형식
    
    Returns:
        DeleteUserResponse: 탈퇴 성공 메시지
    """
    try:
        return user_service.delete_user(db, authorization)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )