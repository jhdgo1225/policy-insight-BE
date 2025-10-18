from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class IssueLegislationAnalysis(Base):
    __tablename__ = "issue_legislation_analysis"

    legislation_analysis_id = Column(String(11), ForeignKey("legislation_analysis.legislation_analysis_id"), primary_key=True, doc="입법 분석 결과의 고유 식별번호")
    issue_id = Column(BigInteger, ForeignKey("issue.issue_id"), primary_key=True, doc="이슈의 고유 식별번호")

    # 관계 설정
    legislation_analysis = relationship("LegislationAnalysis", back_populates="issue_legislation_analyses")
    issue = relationship("Issue", back_populates="issue_legislation_analyses")