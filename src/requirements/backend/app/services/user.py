from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
import re
from app.schemas.user import (
    UserInfoResponse, UpdateUserRequest, 
    UpdateUserResponse, DeleteUserResponse
)
from app.crud import user as user_crud
from app.core.security import (
    verify_access_token,
    get_token_from_header
)


def validate_phone_format(phone: str) -> bool:
    """
    전화번호 형식을 검증합니다.
    조건: 숫자만 11자리
    """
    phone_digits = re.sub(r'[-\s]', '', phone)
    return phone_digits.isdigit() and len(phone_digits) == 11


def get_user_info(db: Session, authorization: str) -> UserInfoResponse:
    """
    사용자 정보를 조회합니다.
    
    Args:
        db: 데이터베이스 세션
        authorization: Authorization 헤더 값 (Bearer {access_token})
        
    Returns:
        UserInfoResponse: 사용자 정보
        
    Raises:
        HTTPException: 인증 실패 또는 조회 실패 시
    """
    # 1. Authorization 헤더에서 토큰 추출
    token = get_token_from_header(authorization)
    
    # 2. 액세스 토큰 검증 및 디코드
    payload = verify_access_token(token)
    
    # 3. 토큰에서 회원 ID 추출
    member_id_str = payload.get("sub")
    if not member_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    try:
        member_id = int(member_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 4. 회원 정보 조회
    member = user_crud.get_member_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 5. 응답 데이터 생성
    return UserInfoResponse(
        id=member.member_id,
        email=member.email,
        name=member.member_name,
        image=member.profile_image,
        phone=member.phone
    )


def update_user_info(
    db: Session, 
    update_data: UpdateUserRequest,
    authorization: str
) -> UpdateUserResponse:
    """
    사용자 정보를 수정합니다.
    
    Args:
        db: 데이터베이스 세션
        update_data: 수정할 사용자 정보
        authorization: Authorization 헤더 값 (Bearer {access_token})
        
    Returns:
        UpdateUserResponse: 수정된 사용자 정보
        
    Raises:
        HTTPException: 인증 실패 또는 수정 실패 시
    """
    # 1. Authorization 헤더에서 토큰 추출
    token = get_token_from_header(authorization)
    
    # 2. 액세스 토큰 검증 및 디코드
    payload = verify_access_token(token)
    
    # 3. 토큰에서 회원 ID 추출
    member_id_str = payload.get("sub")
    if not member_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    try:
        member_id = int(member_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 4. 회원 존재 여부 확인
    member = user_crud.get_member_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 5. 전화번호 형식 검증 (제공된 경우)
    if update_data.phone is not None and not validate_phone_format(update_data.phone):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 6. 전화번호 정규화 (제공된 경우)
    phone_normalized = None
    if update_data.phone is not None:
        phone_normalized = re.sub(r'[-\s]', '', update_data.phone)
    
    # 7. 회원 정보 업데이트
    updated_member = user_crud.update_member_info(
        db=db,
        member_id=member_id,
        image=update_data.image,
        phone=phone_normalized
    )
    
    if not updated_member:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )
    
    # 8. 응답 데이터 생성
    return UpdateUserResponse(
        image=updated_member.profile_image,
        phone=updated_member.phone
    )


def delete_user(db: Session, authorization: str) -> DeleteUserResponse:
    """
    회원 탈퇴를 처리합니다.
    
    Args:
        db: 데이터베이스 세션
        authorization: Authorization 헤더 값 (Bearer {access_token})
        
    Returns:
        DeleteUserResponse: 탈퇴 성공 메시지
        
    Raises:
        HTTPException: 인증 실패 또는 처리 실패 시
    """
    # 1. Authorization 헤더에서 토큰 추출
    token = get_token_from_header(authorization)
    
    # 2. 액세스 토큰 검증 및 디코드
    payload = verify_access_token(token)
    
    # 3. 토큰에서 회원 ID 추출
    member_id_str = payload.get("sub")
    if not member_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    try:
        member_id = int(member_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 4. 회원 존재 여부 확인
    member = user_crud.get_member_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 5. 회원 탈퇴 처리
    if not user_crud.delete_member(db, member_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )
    
    # 6. 성공 응답 반환
    return DeleteUserResponse(message="success")
