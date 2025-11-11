import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError
from fastapi import HTTPException, status, Header
from .config import settings


def hash_password(password: str) -> str:
    """SHA-256 방식으로 비밀번호를 해시화합니다."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시된 비밀번호를 비교합니다."""
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    액세스 토큰을 생성합니다.
    
    Args:
        data: 토큰에 포함할 데이터 (member_id, token_version 필수)
        expires_delta: 만료 시간 (옵션)
    
    Returns:
        생성된 JWT 액세스 토큰
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """리프레시 토큰을 생성합니다."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict]:
    """토큰을 디코드합니다."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_refresh_token(token: str) -> Dict:
    """
    리프레시 토큰을 검증하고 디코드합니다.
    
    Args:
        token: JWT 리프레시 토큰
        
    Returns:
        디코드된 토큰 페이로드
        
    Raises:
        HTTPException: 토큰이 유효하지 않을 경우
    """
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    return payload


def get_token_from_header(authorization: str) -> str:
    """
    Authorization 헤더에서 토큰을 추출합니다.
    
    Args:
        authorization: "Bearer {token}" 형식의 Authorization 헤더 값
        
    Returns:
        추출된 토큰 문자열
        
    Raises:
        HTTPException: 헤더 형식이 올바르지 않을 경우
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    return parts[1]


def verify_access_token(token: str) -> Dict:
    """
    액세스 토큰을 검증하고 디코드합니다.
    
    Args:
        token: JWT 액세스 토큰
        
    Returns:
        디코드된 토큰 페이로드 (member_id, token_version 포함)
        
    Raises:
        HTTPException: 토큰이 유효하지 않을 경우
    """
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # token_version이 포함되어 있는지 확인
    if "token_version" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    return payload
