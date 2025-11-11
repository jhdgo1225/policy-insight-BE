from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.sql import func

from app.core.db import Base


class IssueReport(Base):
    __tablename__ = "issue_report"

    issue_report_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, doc="이슈 리포트 고유번호")
    issue_id = Column(BigInteger, ForeignKey("issue.issue_id"), nullable=False, doc="연관된 이슈 번호")
    report_id = Column(BigInteger, ForeignKey("report.report_id"), nullable=False, doc="연관된 리포트 번호")