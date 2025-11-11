import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 모델을 사용할 수 있도록 import
# 이 import는 Base 정의 후에 와야 합니다
# 회원 관련 모델
from app.models.member import Member
from app.models.login_history import LoginHistory
from app.models.social_account import SocialAccount

# 정책 인사이트 관련 모델
from app.models.news import News
from app.models.law import Law
from app.models.issue import Issue
from app.models.legislation_analysis import LegislationAnalysis
from app.models.issue_legislation_analysis import IssueLegislationAnalysis
from app.models.report import Report
from app.models.data_collection_history import DataCollectionHistory
from app.models.issue_report import IssueReport
