from sqlalchemy import Column, BigInteger, String, TIMESTAMP, Text, CHAR, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.db import Base


class Member(Base):
    __tablename__ = "member"

    member_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, doc="회원 고유 식별번호")
    email = Column(String(100), unique=True, nullable=False, doc="회원의 이메일 주소")
    passwd = Column(String(64), nullable=True, doc="암호화된 패스워드")
    member_name = Column(String(50), nullable=False, doc="회원의 실명")
    phone = Column(String(11), nullable=False, doc="회원 전화번호")
    profile_image = Column(String(500), nullable=False, doc="프로필 이미지 경로")
    join_date = Column(TIMESTAMP, nullable=False, server_default=func.now(), doc="회원 가입 일시")
    refresh_token = Column(Text, nullable=True, doc="리프레시 토큰 정보")
    token_version = Column(BigInteger, nullable=False, server_default='1', doc="토큰 버전 (리프레시 시 증가)")
    last_login = Column(TIMESTAMP, nullable=True, doc="최종 로그인 일시")
    account_status = Column(CHAR(1), nullable=False, server_default='A', doc="계정의 현재 상태")  # A:활성, S:정지, W:탈퇴
    withdrawal_date = Column(TIMESTAMP, nullable=True, doc="회원 탈퇴 일시")

    # 관계 설정 - 역참조
    login_histories = relationship("LoginHistory", back_populates="member", cascade="all, delete-orphan")
    social_accounts = relationship("SocialAccount", back_populates="member", cascade="all, delete-orphan")