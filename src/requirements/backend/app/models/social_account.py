from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, CHAR, Boolean, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.db import Base


class SocialAccount(Base):
    __tablename__ = "social_account"

    social_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, doc="소셜 연동의 고유 식별번호")
    member_id = Column(BigInteger, ForeignKey("member.member_id"), nullable=False, doc="연동된 회원 번호")
    social_platform = Column(String(50), nullable=False, doc="소셜 플랫폼명")  # G: Google, K: Kakao, N: Naver
    social_account_id = Column(String(200), nullable=False, doc="소셜 플랫폼의 계정 ID")
    linked_date = Column(TIMESTAMP, nullable=False, server_default=func.now(), doc="계정 연동 일시")
    link_status = Column(CHAR(1), nullable=False, server_default='A', doc="연동 상태")  # A:활성, D:해제
    profile_sync = Column(Boolean, nullable=False, server_default='false', doc="프로필 동기화 여부")  # TRUE:동기화, FALSE:비동기화

    # 관계 설정
    member = relationship("Member", back_populates="social_accounts")