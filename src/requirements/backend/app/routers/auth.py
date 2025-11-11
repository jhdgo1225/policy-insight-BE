from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.schemas.auth import (
    LoginRequest, LoginResponse, 
    LogoutResponse, SignupRequest, SignupResponse,
    RefreshTokenRequest, RefreshTokenResponse, ResetPasswordNoLoginRequest,
    ResetPasswordLoginRequest, PasswordChangeResponse,
    PasswordHistoryItem, FindIdRequest, FindIdResponse,
    ErrorResponse
)
from app.services import auth as auth_service
from app.core.dependencies import get_token_from_credentials


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
	token: str = Depends(get_token_from_credentials),
	db: Session = Depends(get_db)
):
	"""
	로그아웃 API
	
	액세스 토큰을 검증하고 사용자의 토큰을 무효화합니다.
	
	- **Authorization Header**: Swagger UI의 Authorize 버튼을 통해 액세스 토큰 입력
	
	Returns:
		LogoutResponse: 로그아웃 성공 메시지
	"""
	try:
		return auth_service.logout_user(db, token)
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
	refresh_data: RefreshTokenRequest,
	db: Session = Depends(get_db)
):
	"""
	리프레시 토큰을 통한 액세스 토큰 재발급 API
	
	리프레시 토큰을 검증하고 새로운 액세스 토큰을 발급합니다.
	
	Request Body:
	- **refreshToken**: 리프레시 토큰 (Bearer 접두사 없이 토큰만 입력)
	
	Returns:
		RefreshTokenResponse: 새로 발급된 액세스 토큰
	"""
	try:
		# Bearer 접두사를 추가하여 서비스 레이어로 전달
		token_with_bearer = f"Bearer {refresh_data.refreshToken}"
		return auth_service.refresh_access_token(db, token_with_bearer)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server error"
		)

@router.put(
	'/password/nologin',
	response_model=PasswordChangeResponse,
	status_code=status.HTTP_200_OK,
	responses={
		401: {"model": ErrorResponse, "description": "Unauthorized"},
		500: {"model": ErrorResponse, "description": "Internal server error"}
	}
)
async def reset_password_nologin(
	reset_data: ResetPasswordNoLoginRequest,
	db: Session = Depends(get_db)
):
	"""
	비로그인 상태에서 비밀번호 변경 API
	
	이메일(ID)과 새 비밀번호를 통해 비밀번호를 변경합니다.
	
	- **id**: 회원의 이메일 주소 (ID)
	- **password**: 새 비밀번호 (10-20자, 영대문자, 영소문자, 숫자, 특수문자 최소 1개 이상 포함)
	
	Returns:
		PasswordChangeResponse: 비밀번호 변경 성공 메시지
	"""
	try:
		return auth_service.reset_password_nologin(db, reset_data)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server error"
		)

@router.put(
	'/password/login',
	response_model=List[PasswordHistoryItem],
	status_code=status.HTTP_200_OK,
	responses={
		401: {"model": ErrorResponse, "description": "Unauthorized"},
		500: {"model": ErrorResponse, "description": "Internal server error"}
	}
)
async def reset_password_login(
	reset_data: ResetPasswordLoginRequest,
	token: str = Depends(get_token_from_credentials),
	db: Session = Depends(get_db)
):
	"""
	로그인 상태에서 비밀번호 변경 API
	
	액세스 토큰을 검증하고 새 비밀번호로 변경합니다.
	
	- **Authorization Header**: Swagger UI의 Authorize 버튼을 통해 액세스 토큰 입력
	- **password**: 새 비밀번호 (10-20자, 영대문자, 영소문자, 숫자, 특수문자 최소 1개 이상 포함)
	
	Returns:
		List[PasswordHistoryItem]: 비밀번호 변경 이력 목록
	"""
	try:
		return auth_service.reset_password_login(db, reset_data, token)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server error"
		)

@router.post(
	'/id',
	response_model=FindIdResponse,
	status_code=status.HTTP_200_OK,
	responses={
		401: {"model": ErrorResponse, "description": "Unauthorized"},
		500: {"model": ErrorResponse, "description": "Internal server error"}
	}
)
async def find_id(
	find_data: FindIdRequest,
	db: Session = Depends(get_db)
):
	"""
	아이디 찾기 API
	
	이메일을 통해 아이디(이메일)를 조회합니다.
	
	- **email**: 회원의 이메일 주소
	
	Returns:
		FindIdResponse: 찾은 아이디(이메일)
	"""
	try:
		return auth_service.find_user_id(db, find_data)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Server error"
		)
