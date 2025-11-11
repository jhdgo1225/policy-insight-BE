from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional
from app.models.member import Member


def get_member_by_id(db: Session, member_id: int) -> Optional[Member]:
    """회원 ID로 회원 정보를 조회합니다."""
    return db.query(Member).filter(
        Member.member_id == member_id,
        Member.account_status == 'A'  # 활성 상태인 계정만
    ).first()


def update_member_info(
    db: Session,
    member_id: int,
    image: Optional[str] = None,
    phone: Optional[str] = None
) -> Optional[Member]:
    """
    회원 정보를 업데이트합니다.
    
    Args:
        db: 데이터베이스 세션
        member_id: 회원 ID
        image: 프로필 이미지 경로 (선택)
        phone: 전화번호 (선택)
        
    Returns:
        업데이트된 회원 객체
    """
    member = db.query(Member).filter(Member.member_id == member_id).first()
    if member:
        if image is not None:
            member.profile_image = image
        if phone is not None:
            member.phone = phone
        db.commit()
        db.refresh(member)
    return member


def delete_member(db: Session, member_id: int) -> bool:
    """
    회원을 탈퇴 처리합니다 (계정 상태를 'W'로 변경).
    
    Args:
        db: 데이터베이스 세션
        member_id: 회원 ID
        
    Returns:
        성공 여부
    """
    member = db.query(Member).filter(Member.member_id == member_id).first()
    if member:
        member.account_status = 'W'  # 탈퇴 상태
        member.withdrawal_date = func.now()  # 탈퇴 일시 기록
        member.refresh_token = None  # 리프레시 토큰 삭제
        db.commit()
        return True
    return False
