from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Optional, List
import re
from datetime import datetime
from app.schemas.auth import (
    LoginRequest, LoginResponse, 
    LogoutResponse, SignupRequest, SignupResponse,
    RefreshTokenResponse, ResetPasswordNoLoginRequest, 
    ResetPasswordLoginRequest, PasswordChangeResponse,
    PasswordHistoryItem, FindIdRequest, FindIdResponse
)
from app.crud import auth as auth_crud
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
    get_token_from_header
)


def validate_email_format(email: str) -> bool:
    """이메일 형식을 검증합니다."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def validate_password_format(password: str) -> bool:
    """
    비밀번호 형식을 검증합니다.
    조건: 
    - 길이: 10-20자
    - 영대문자, 영소문자, 숫자, 특수문자가 최소 1개 이상 포함
    """
    # 길이 검증
    if len(password) < 10 or len(password) > 20:
        return False
    
    # 문자 조합 검증
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[^\w\s]', password))
    
    return has_upper and has_lower and has_digit and has_special


def validate_name_format(name: str) -> bool:
    """
    이름 형식을 검증합니다.
    조건: 1-50자, 공백 제외 최소 1자 이상
    """
    if not name or len(name.strip()) == 0:
        return False
    if len(name) > 50:
        return False
    return True


def validate_phone_format(phone: str) -> bool:
    """
    전화번호 형식을 검증합니다.
    조건: 숫자만 11자리
    """
    phone_digits = re.sub(r'[-\s]', '', phone)
    return phone_digits.isdigit() and len(phone_digits) == 11


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
    
    # 6. 토큰 생성 (token_version 포함)
    token_data = {
        "sub": str(member.member_id), 
        "email": member.email,
        "token_version": member.token_version or 1
    }
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
    
    # 5. 토큰 버전 확인
    token_version = payload.get("token_version")
    if token_version != member.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 6. 계정 상태 확인
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


def signup_user(db: Session, signup_data: SignupRequest) -> SignupResponse:
    """
    사용자 회원가입을 처리합니다.
    
    Args:
        db: 데이터베이스 세션
        signup_data: 회원가입 요청 데이터
        
    Returns:
        SignupResponse: 회원가입 성공 응답
        
    Raises:
        HTTPException: 유효성 검사 실패 또는 중복 가입 시
    """
    # 1. 이메일 형식 검증
    if not validate_email_format(signup_data.email):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 2. 이메일 중복 확인
    if auth_crud.check_email_exists(db, signup_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # 3. 비밀번호 형식 검증
    if not validate_password_format(signup_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 4. 이름 형식 검증
    if not validate_name_format(signup_data.name):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 5. 전화번호 형식 검증
    if not validate_phone_format(signup_data.phone):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 6. 비밀번호 해싱
    hashed_password = hash_password(signup_data.password)
    
    # 7. 전화번호 정규화 (하이픈 제거)
    phone_normalized = re.sub(r'[-\s]', '', signup_data.phone)
    
    # 8. 회원 생성
    try:
        new_member = auth_crud.create_member(
            db=db,
            email=signup_data.email,
            hashed_password=hashed_password,
            name=signup_data.name,
            phone=phone_normalized
            # profile_image는 CRUD에서 자동으로 /static/profiles/{member_id}/profile.png로 설정됨
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )
    
    # 9. 성공 응답 반환
    return SignupResponse(message="success")


def refresh_access_token(db: Session, authorization: str) -> RefreshTokenResponse:
    """
    리프레시 토큰을 이용하여 새로운 액세스 토큰을 발급합니다.
    
    Args:
        db: 데이터베이스 세션
        authorization: Authorization 헤더 값 (Bearer {refresh_token})
        
    Returns:
        RefreshTokenResponse: 새로 발급된 액세스 토큰
        
    Raises:
        HTTPException: 인증 실패 또는 처리 실패 시
    """
    # 1. Authorization 헤더에서 리프레시 토큰 추출
    refresh_token = get_token_from_header(authorization)
    
    # 2. 리프레시 토큰 검증 및 디코드
    payload = verify_refresh_token(refresh_token)
    
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
    
    # 4. 리프레시 토큰으로 회원 조회
    member = auth_crud.get_member_by_refresh_token(db, refresh_token)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 5. 회원 ID 일치 확인
    if member.member_id != member_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 6. 계정 상태 확인
    if member.account_status != 'A':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 7. 토큰 버전 증가 (기존 액세스 토큰 무효화)
    updated_member = auth_crud.increment_token_version(db, member.member_id)
    
    # 8. 새로운 액세스 토큰 생성 (새로운 token_version 포함)
    token_data = {
        "sub": str(member.member_id), 
        "email": member.email,
        "token_version": updated_member.token_version
    }
    new_access_token = create_access_token(token_data)
    
    # 9. 성공 응답 반환
    return RefreshTokenResponse(accessToken=new_access_token)


def reset_password_nologin(db: Session, reset_data: ResetPasswordNoLoginRequest) -> PasswordChangeResponse:
    """
    비로그인 상태에서 비밀번호를 변경합니다.
    
    Args:
        db: 데이터베이스 세션
        reset_data: 비밀번호 변경 요청 데이터
        
    Returns:
        PasswordChangeResponse: 비밀번호 변경 성공 응답
        
    Raises:
        HTTPException: 유효성 검사 실패 또는 처리 실패 시
    """
    # 1. 이메일 형식 검증
    if not validate_email_format(reset_data.id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 2. 비밀번호 형식 검증
    if not validate_password_format(reset_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 3. 이메일로 회원 조회
    member = auth_crud.get_member_by_email(db, reset_data.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 4. 계정 상태 확인
    if member.account_status != 'A':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 5. 비밀번호 해싱
    hashed_password = hash_password(reset_data.password)
    
    # 6. 비밀번호 업데이트
    if not auth_crud.update_password(db, member.member_id, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )
    
    # 7. 성공 응답 반환
    return PasswordChangeResponse(message="success")


def reset_password_login(
    db: Session, 
    reset_data: ResetPasswordLoginRequest,
    authorization: str
) -> List[PasswordHistoryItem]:
    """
    로그인 상태에서 비밀번호를 변경합니다.
    
    Args:
        db: 데이터베이스 세션
        reset_data: 비밀번호 변경 요청 데이터
        authorization: Authorization 헤더 값 (Bearer {access_token})
        
    Returns:
        List[PasswordHistoryItem]: 비밀번호 변경 이력 목록
        
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
    
    # 5. 토큰 버전 확인
    token_version = payload.get("token_version")
    if token_version != member.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 6. 계정 상태 확인
    if member.account_status != 'A':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 7. 비밀번호 형식 검증
    if not validate_password_format(reset_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 8. 비밀번호 해싱
    hashed_password = hash_password(reset_data.password)
    
    # 9. 비밀번호 업데이트
    if not auth_crud.update_password(db, member.member_id, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        )
    
    # 10. 비밀번호 변경 이력 반환 (현재 변경 내역)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history = [
        PasswordHistoryItem(
            title="비밀번호 변경",
            date=current_time
        )
    ]
    
    return history


def find_user_id(db: Session, find_data: FindIdRequest) -> FindIdResponse:
    """
    이메일로 아이디(이메일)를 찾습니다.
    
    Args:
        db: 데이터베이스 세션
        find_data: 아이디 찾기 요청 데이터
        
    Returns:
        FindIdResponse: 찾은 아이디(이메일)
        
    Raises:
        HTTPException: 유효성 검사 실패 또는 조회 실패 시
    """
    # 1. 이메일 형식 검증
    if not validate_email_format(find_data.email):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 2. 이메일로 회원 조회
    member = auth_crud.get_member_by_email(db, find_data.email)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 3. 계정 상태 확인
    if member.account_status != 'A':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # 4. 아이디(이메일) 반환
    return FindIdResponse(id=member.email)
