from sqlalchemy import Column, String, Text, TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class News(Base):
    __tablename__ = "news"

    news_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, doc="뉴스의 고유 식별번호")
    news_title = Column(String(500), nullable=False, doc="뉴스 제목")
    body = Column(Text, nullable=False, doc="뉴스 본문 내용")
    summary = Column(Text, nullable=True, doc="뉴스 요약 내용")
    category = Column(Text, nullable=False, doc="뉴스의 카테고리")
    sub_category = Column(Text, nullable=False, doc="카테고리의 상세 카테고리")
    published = Column(TIMESTAMP, nullable=False, doc="뉴스 게시 일시")
    company = Column(Text, nullable=False, doc="신문사")  # 1: 한국경제, 2: 세계일보, 3: 조선일보, 4: 중앙일보, 5: 문화일보, 6: 아시아투데이
    news_url = Column(String(1000), nullable=False, server_default=func.now(), doc="뉴스 원문 URL")
    issue_id = Column(BigInteger, ForeignKey("issue.issue_id"), nullable=True, doc="연관된 이슈 번호")
    collection_id = Column(BigInteger, ForeignKey("data_collection_history.collection_id"), nullable=True, doc="데이터 수집 이력 코드")

    # 관계 설정
    issue = relationship("Issue", back_populates="news")
    data_collection = relationship("DataCollectionHistory", back_populates="news")