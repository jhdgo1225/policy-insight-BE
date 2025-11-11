from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional


security = HTTPBearer()


def get_token_from_credentials(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    HTTPBearer를 통해 토큰을 추출합니다.
    
    Args:
        credentials: HTTP Authorization 크레덴셜
        
    Returns:
        Bearer 토큰 문자열 (전체 "Bearer {token}" 형식)
        
    Raises:
        HTTPException: 인증 실패 시
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorize"
        )
    
    # "Bearer {token}" 형식으로 반환 (기존 서비스 로직과 호환)
    return f"Bearer {credentials.credentials}"
