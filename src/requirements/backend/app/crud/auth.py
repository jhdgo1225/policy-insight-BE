from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional
from app.models.member import Member
from app.models.login_history import LoginHistory


def get_member_by_email(db: Session, email: str) -> Optional[Member]:
    """이메일로 회원 정보를 조회합니다."""
    return db.query(Member).filter(Member.email == email).first()


def get_member_by_id(db: Session, member_id: int) -> Optional[Member]:
    """회원 ID로 회원 정보를 조회합니다."""
    return db.query(Member).filter(Member.member_id == member_id).first()


def get_member_by_refresh_token(db: Session, refresh_token: str) -> Optional[Member]:
    """리프레시 토큰으로 회원 정보를 조회합니다."""
    return db.query(Member).filter(
        Member.refresh_token == refresh_token,
        Member.account_status == 'A'  # 활성 상태인 계정만
    ).first()


def check_email_exists(db: Session, email: str) -> bool:
    """이메일이 이미 존재하는지 확인합니다."""
    return db.query(Member).filter(Member.email == email).first() is not None


def create_member(
    db: Session,
    email: str,
    hashed_password: str,
    name: str,
    phone: str,
    profile_image: str = "default_profile.png"
) -> Member:
    """
    새로운 회원을 생성합니다.
    
    Args:
        db: 데이터베이스 세션
        email: 회원 이메일
        hashed_password: 해시된 비밀번호
        name: 회원 이름
        phone: 전화번호
        profile_image: 프로필 이미지 경로 (기본값: default_profile.png)
        
    Returns:
        생성된 회원 객체
    """
    new_member = Member(
        email=email,
        passwd=hashed_password,
        member_name=name,
        phone=phone,
        profile_image=profile_image,
        account_status='A'  # 활성 상태
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


def update_refresh_token(db: Session, member_id: int, refresh_token: str) -> Member:
    """리프레시 토큰을 업데이트합니다."""
    member = db.query(Member).filter(Member.member_id == member_id).first()
    if member:
        member.refresh_token = refresh_token
        member.last_login = func.now()
        db.commit()
        db.refresh(member)
    return member


def invalidate_tokens(db: Session, member_id: int) -> bool:
    """
    회원의 리프레시 토큰을 무효화합니다.
    
    Args:
        db: 데이터베이스 세션
        member_id: 회원 ID
        
    Returns:
        성공 여부
    """
    member = db.query(Member).filter(Member.member_id == member_id).first()
    if member:
        member.refresh_token = None
        db.commit()
        return True
    return False


def create_login_history(
    db: Session,
    member_id: int,
    access_ip: Optional[str] = None,
    access_device: Optional[str] = None,
    browser_info: Optional[str] = None
) -> LoginHistory:
    """로그인 기록을 생성합니다."""
    login_history = LoginHistory(
        member_id=member_id,
        access_ip=access_ip,
        access_device=access_device,
        browser_info=browser_info
    )
    db.add(login_history)
    db.commit()
    db.refresh(login_history)
    return login_history


def update_logout_date(db: Session, member_id: int) -> bool:
    """
    가장 최근 로그인 기록에 로그아웃 일시를 업데이트합니다.
    
    Args:
        db: 데이터베이스 세션
        member_id: 회원 ID
        
    Returns:
        성공 여부
    """
    # 가장 최근 로그인 기록 중 로그아웃 일시가 없는 것을 찾아 업데이트
    login_history = db.query(LoginHistory).filter(
        LoginHistory.member_id == member_id,
        LoginHistory.logout_date.is_(None)
    ).order_by(LoginHistory.login_date.desc()).first()
    
    if login_history:
        login_history.logout_date = func.now()
        db.commit()
        return True
    return False


def verify_member_credentials(db: Session, email: str, hashed_password: str) -> Optional[Member]:
    """이메일과 해시된 비밀번호로 회원을 검증합니다."""
    return db.query(Member).filter(
        Member.email == email,
        Member.passwd == hashed_password,
        Member.account_status == 'A'  # 활성 상태인 계정만
    ).first()
