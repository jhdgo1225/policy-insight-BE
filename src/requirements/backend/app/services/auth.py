from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Optional
import re
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse
from app.crud import auth as auth_crud
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_access_token,
    get_token_from_header
)


def validate_email_format(email: str) -> bool:
    """이메일 형식을 검증합니다."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_password_format(password: str) -> bool:
    """
    비밀번호 형식을 검증합니다.
    조건: 영대문자, 영소문자, 숫자, 특수문자가 최소 1개 이상 포함
    """
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[^\w\s]', password))
    
    return has_upper and has_lower and has_digit and has_special


def parse_user_agent(user_agent: str) -> tuple[Optional[str], Optional[str]]:
    """
    User-Agent 문자열에서 디바이스와 브라우저 정보를 추출합니다.
    
    Args:
        user_agent: User-Agent 문자열
        
    Returns:
        (디바이스 정보, 브라우저 정보) 튜플
    """
    if not user_agent:
        return None, None
    
    # 디바이스 정보 추출
    device = None
    if "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent:
        if "iPhone" in user_agent:
            device = "iPhone"
        elif "iPad" in user_agent:
            device = "iPad"
        elif "Android" in user_agent:
            device = "Android"
        else:
            device = "Mobile"
    elif "Windows" in user_agent:
        device = "Windows"
    elif "Macintosh" in user_agent or "Mac OS" in user_agent:
        device = "Mac"
    elif "Linux" in user_agent:
        device = "Linux"
    else:
        device = "Unknown"
    
    # 브라우저 정보는 전체 User-Agent를 저장 (최대 300자)
    browser_info = user_agent[:300] if len(user_agent) > 300 else user_agent
    
    return device, browser_info


def login_user(
    db: Session, 
    login_data: LoginRequest,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None
) -> LoginResponse:
    """
    사용자 로그인을 처리합니다.
    
    Args:
        db: 데이터베이스 세션
        login_data: 로그인 요청 데이터
        
    Returns:
        LoginResponse: 로그인 응답 데이터
        
    Raises:
        HTTPException: 유효성 검사 실패 또는 인증 실패 시
    """
    # 1. 이메일 형식 검증
    if not validate_email_format(login_data.email):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid authorize"
        )
    
    # 2. 비밀번호 형식 검증
    if not validate_password_format(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid authorize"
        )
    
    # 3. 이메일로 회원 조회
    member = auth_crud.get_member_by_email(db, login_data.email)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid authorize"
        )
    
    # 4. 계정 상태 확인
    if member.account_status != 'A':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid authorize"
        )
    
    # 5. 비밀번호 검증
    hashed_password = hash_password(login_data.password)
    if member.passwd != hashed_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid authorize"
        )
    
    # 6. 토큰 생성
    token_data = {"sub": str(member.member_id), "email": member.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # 7. 리프레시 토큰 DB 업데이트
    updated_member = auth_crud.update_refresh_token(db, member.member_id, refresh_token)
    
    # 8. User-Agent에서 디바이스 및 브라우저 정보 추출
    access_device, browser_info = parse_user_agent(user_agent)
    
    # 9. 로그인 기록 생성
    auth_crud.create_login_history(
        db=db,
        member_id=member.member_id,
        access_ip=client_ip,
        access_device=access_device,
        browser_info=browser_info
    )
    
    # 10. 응답 데이터 생성
    return LoginResponse(
        id=updated_member.member_id,
        accessToken=access_token,
        refreshToken=refresh_token,
        email=updated_member.email,
        name=updated_member.member_name,
        image=updated_member.profile_image,
        phone=updated_member.phone
    )


def logout_user(db: Session, authorization: str) -> LogoutResponse:
    """
    사용자 로그아웃을 처리합니다.
    
    Args:
        db: 데이터베이스 세션
        authorization: Authorization 헤더 값 (Bearer {access_token})
        
    Returns:
        LogoutResponse: 로그아웃 성공 응답
        
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
    member = auth_crud.get_member_by_id(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 5. 계정 상태 확인
    if member.account_status != 'A':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 6. 토큰 무효화 (리프레시 토큰 삭제)
    if not auth_crud.invalidate_tokens(db, member_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )
    
    # 7. 로그아웃 일시 업데이트 (로그인 기록 테이블)
    auth_crud.update_logout_date(db, member_id)
    
    # 8. 성공 응답 반환
    return LogoutResponse(message="success")
