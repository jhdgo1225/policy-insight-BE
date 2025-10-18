from sqlalchemy import Column, String, CHAR, TIMESTAMP, BigInteger, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import BIGSERIAL

from app.db.base import Base


class Report(Base):
    __tablename__ = "report"

    report_id = Column(BigInteger, primary_key=True, index=True, server_default=func.nextval('report_report_id_seq'), doc="리포트의 고유 식별번호")
    issue_id = Column(BigInteger, ForeignKey("issue.issue_id"), nullable=False, doc="관련된 이슈 번호")
    report_name = Column(String(200), nullable=False, doc="리포트의 명칭")
    report_type = Column(CHAR(1), nullable=False, doc="리포트의 유형")
    created_date = Column(TIMESTAMP, nullable=False, server_default=func.now(), doc="리포트 생성 일시")

    __table_args__ = (
        CheckConstraint("report_type IN ('D', 'W', 'M')", name='check_report_type'),
    )

    # 관계 설정
    issues = relationship("Issue", secondary="issue_report", back_populates="reports")