from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BIGSERIAL

from app.db.base import Base


class LoginHistory(Base):
    __tablename__ = "login_history"

    history_id = Column(BigInteger, primary_key=True, index=True, server_default=func.nextval('login_history_history_id_seq'), doc="로그인 기록의 고유 식별번호")
    member_id = Column(BigInteger, ForeignKey("member.member_id"), nullable=False, doc="로그인한 회원 번호")
    login_date = Column(TIMESTAMP, nullable=False, server_default=func.now(), doc="로그인 일시")
    logout_date = Column(TIMESTAMP, nullable=True, doc="로그아웃 일시")
    access_ip = Column(String(45), nullable=True, doc="접속한 IP 주소")  # IPv4, IPv6 지원
    access_device = Column(String(200), nullable=True, doc="접속한 기기 정보")
    browser_info = Column(String(300), nullable=True, doc="사용한 브라우저 정보")
    failure_reason = Column(String(200), nullable=True, doc="로그인 실패 사유")

    # 관계 설정
    member = relationship("Member", back_populates="login_histories")