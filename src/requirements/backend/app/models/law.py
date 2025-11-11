from sqlalchemy import Column, String, Text, Date
from sqlalchemy.orm import relationship

from app.core.db import Base


class Law(Base):
    __tablename__ = "law"

    law_id = Column(String(6), primary_key=True, index=True, doc="법령 고유 식별번호")
    proclamation_date = Column(Date, nullable=False, doc="법령 공포 일자")
    law_type_code = Column(String(10), nullable=False, doc="법령 종류 구분 코드")
    law_name = Column(String(500), nullable=False, doc="법령 명칭")
    ministry_code = Column(String(10), nullable=False, doc="소관 부처 코드")
    enforcement_date = Column(Date, nullable=True, doc="법령 시행 일자")
    revision_type = Column(String(20), nullable=True, doc="제정/개정 구분")
    law_file_path = Column(Text, nullable=True, doc="법령 파일 저장 경로")

    # 관계 설정
    issues = relationship("Issue", back_populates="law")
    legislation_analyses = relationship("LegislationAnalysis", back_populates="law")