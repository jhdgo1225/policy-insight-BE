from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.auth import (
    LoginRequest, LoginResponse, 
    LogoutResponse, SignupRequest, SignupResponse,
    RefreshTokenResponse, ErrorResponse
)
from app.services import auth as auth_service


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post(
	'/login',
	response_model=LoginResponse,
	status_code=status.HTTP_200_OK,
	responses={
		404: {"model": ErrorResponse, "description": "Invalid authorize"},
		500: {"model": ErrorResponse, "description": "Server error"}
	}
)
async def login(
	login_data: LoginRequest,
	request: Request,
	db: Session = Depends(get_db)
):
	"""
	로그인 API
	
	이메일과 비밀번호를 통해 로그인을 수행하고, JWT 토큰을 발급합니다.
	
	- **email**: 회원의 이메일 주소 (이메일 형식)
	- **password**: 비밀번호 (10-20자, 영대문자, 영소문자, 숫자, 특수문자 최소 1개 이상 포함)
	
	Returns:
		LoginResponse: 회원 정보 및 JWT 토큰
	"""
	try:
		# 클라이언트 IP 추출
		client_ip = request.client.host if request.client else None
		
		# User-Agent 추출
		user_agent = request.headers.get("user-agent", "")
		
		return auth_service.login_user(db, login_data, client_ip, user_agent)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server error"
		)

@router.post(
	'/logout',
	response_model=LogoutResponse,
	status_code=status.HTTP_200_OK,
	responses={
		401: {"model": ErrorResponse, "description": "Unauthorized"},
		500: {"model": ErrorResponse, "description": "Internal server error"}
	}
)
async def logout(
	authorization: str = Header(..., description="Bearer {access_token}"),
	db: Session = Depends(get_db)
):
	"""
	로그아웃 API
	
	액세스 토큰을 검증하고 사용자의 토큰을 무효화합니다.
	
	- **Authorization Header**: Bearer {access_token} 형식
	
	Returns:
		LogoutResponse: 로그아웃 성공 메시지
	"""
	try:
		return auth_service.logout_user(db, authorization)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server error"
		)

@router.post(
	'/signup',
	response_model=SignupResponse,
	status_code=status.HTTP_201_CREATED,
	responses={
		401: {"model": ErrorResponse, "description": "Unauthorized"},
		500: {"model": ErrorResponse, "description": "Internal server error"}
	}
)
async def signup(
	signup_data: SignupRequest,
	db: Session = Depends(get_db)
):
	"""
	회원가입 API
	
	이메일, 비밀번호, 이름, 전화번호를 통해 회원가입을 수행합니다.
	
	- **email**: 회원의 이메일 주소 (이메일 형식, 중복 불가)
	- **password**: 비밀번호 (10-20자, 영대문자, 영소문자, 숫자, 특수문자 최소 1개 이상 포함)
	- **name**: 회원의 실명 (1-50자)
	- **phone**: 전화번호 (숫자 11자리)
	
	Returns:
		SignupResponse: 회원가입 성공 메시지
	"""
	try:
		return auth_service.signup_user(db, signup_data)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server error"
		)

@router.post(
	'/refresh',
	response_model=RefreshTokenResponse,
	status_code=status.HTTP_201_CREATED,
	responses={
		401: {"model": ErrorResponse, "description": "Unauthorized"},
		500: {"model": ErrorResponse, "description": "Internal server error"}
	}
)
async def create_refresh(
	authorization: str = Header(..., description="Bearer {refresh_token}"),
	db: Session = Depends(get_db)
):
	"""
	리프레시 토큰을 통한 액세스 토큰 재발급 API
	
	리프레시 토큰을 검증하고 새로운 액세스 토큰을 발급합니다.
	
	- **Authorization Header**: Bearer {refresh_token} 형식
	
	Returns:
		RefreshTokenResponse: 새로 발급된 액세스 토큰
	"""
	try:
		return auth_service.refresh_access_token(db, authorization)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server error"
		)

@router.put('/password/nologin')
async def reset_password_nologin(db: Session = Depends(get_db)):
	pass

@router.post('/id')
async def find_id(db: Session = Depends(get_db)):
	pass

@router.put('/password/login')
async def reset_password_login(db: Session = Depends(get_db)):
	pass

@router.get('/me')
async def read_user_info(db: Session = Depends(get_db)):
	pass

@router.put('/me')
async def update_user_info(db: Session = Depends(get_db)):
	pass

@router.delete('/me')
async def delete_user_info(db: Session = Depends(get_db)):
	pass