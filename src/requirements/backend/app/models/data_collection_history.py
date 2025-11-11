from sqlalchemy import Column, CHAR, TIMESTAMP, Integer, Boolean, Text, BigInteger, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.db import Base


class DataCollectionHistory(Base):
    __tablename__ = "data_collection_history"

    collection_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, doc="수집 작업의 고유 식별번호")
    data_type = Column(CHAR(1), nullable=False, doc="수집한 데이터 유형")
    start_date = Column(TIMESTAMP, nullable=False, doc="작업 시작 일시")
    end_date = Column(TIMESTAMP, nullable=True, doc="작업 종료 일시")
    collected_count = Column(Integer, nullable=True, server_default='0', doc="수집된 데이터 건수")
    success_flag = Column(Boolean, nullable=False, server_default='true', doc="작업 성공 여부")
    error_content = Column(Text, nullable=True, doc="작업 실패 시 오류 내용")

    __table_args__ = (
        CheckConstraint("data_type IN ('N')", name='check_data_type'),
    )

    # 관계 설정
    news = relationship("News", back_populates="data_collection")