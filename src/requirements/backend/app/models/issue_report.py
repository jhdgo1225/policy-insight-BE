from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import BIGSERIAL

from app.db.base import Base


class IssueReport(Base):
    __tablename__ = "issue_report"

    issue_report_id = Column(BigInteger, primary_key=True, index=True, server_default=func.nextval('issue_report_issue_report_id_seq'), doc="이슈 리포트 고유번호")
    issue_id = Column(BigInteger, ForeignKey("issue.issue_id"), nullable=False, doc="연관된 이슈 번호")
    report_id = Column(BigInteger, ForeignKey("report.report_id"), nullable=False, doc="연관된 리포트 번호")