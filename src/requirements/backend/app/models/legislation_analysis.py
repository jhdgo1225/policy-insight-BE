from sqlalchemy import Column, String, Text, CHAR, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class LegislationAnalysis(Base):
    __tablename__ = "legislation_analysis"

    legislation_analysis_id = Column(String(11), primary_key=True, index=True, doc="입법 분석 결과의 고유 식별번호")
    law_id = Column(String(6), ForeignKey("law.law_id"), nullable=False, doc="입법 법령명")
    legislation_type = Column(CHAR(1), nullable=False, doc="입법의 유형(제정, 개정, 폐지)")
    legislation_reason = Column(Text, nullable=False, doc="입법 분석 결과의 사유")

    __table_args__ = (
        CheckConstraint("legislation_type IN ('E', 'A', 'R')", name='check_legislation_type'),
    )

    # 관계 설정
    law = relationship("Law", back_populates="legislation_analyses")
    issue_legislation_analyses = relationship("IssueLegislationAnalysis", back_populates="legislation_analysis")