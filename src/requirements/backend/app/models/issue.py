from sqlalchemy import Column, String, Text, TIMESTAMP, Integer, Float, BigInteger, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BIGSERIAL

from app.db.base import Base


class Issue(Base):
    __tablename__ = "issue"

    issue_id = Column(BigInteger, primary_key=True, index=True, server_default=func.nextval('issue_issue_id_seq'), doc="이슈의 고유 식별번호")
    issue_name = Column(String(200), nullable=False, doc="이슈의 명칭")
    issue_description = Column(Text, nullable=True, doc="이슈의 상세 설명")
    keywords = Column(String(500), nullable=True, doc="이슈 관련 키워드")
    occurrence_date = Column(TIMESTAMP, nullable=True, doc="이슈 발생 기간")
    related_news_count = Column(Integer, nullable=True, server_default='0', doc="관련 뉴스 건수")
    news_sentiment = Column(Float, nullable=True, doc="뉴스 기반 감성 지수")
    law_id = Column(String(6), ForeignKey("law.law_id"), nullable=True, doc="관련 법안 번호")
    law_score = Column(Float, nullable=True, doc="법안과의 연관도")

    __table_args__ = (
        CheckConstraint('news_sentiment >= 0 AND news_sentiment <= 1', name='check_news_sentiment_range'),
        CheckConstraint('law_score >= 0 AND law_score <= 1', name='check_law_score_range'),
    )

    # 관계 설정
    law = relationship("Law", back_populates="issues")
    news = relationship("News", back_populates="issue")
    reports = relationship("Report", secondary="issue_report", back_populates="issues")
    issue_legislation_analyses = relationship("IssueLegislationAnalysis", back_populates="issue")