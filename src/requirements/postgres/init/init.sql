-- 스키마 생성
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

-- 스키마 권한 설정
ALTER SCHEMA public OWNER TO admin;

-- ==========================
-- 회원 테이블
-- ==========================
CREATE TABLE members (
    user_no SERIAL PRIMARY KEY,  -- 회원 고유 식별번호, 자동증가
    email VARCHAR(100) NOT NULL UNIQUE,  -- 회원 이메일
    passwd VARCHAR(255) NOT NULL,  -- 암호화된 비밀번호
    user_name VARCHAR(50) NOT NULL,  -- 회원 실명
    profile_image VARCHAR(500),  -- 프로필 이미지 경로
    join_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 가입일시
    last_login TIMESTAMP,  -- 최종 로그인 일시
    account_status CHAR(1) NOT NULL DEFAULT 'A',  -- 계정 상태 (A:활성, S:정지, W:탈퇴)
    permission_level CHAR(1) NOT NULL DEFAULT 'U',  -- 권한 등급 (A:관리자, M:매니저, U:일반사용자)
    permission_date TIMESTAMP,  -- 권한 등급 부여 일시
    permission_granter VARCHAR(50),  -- 권한 부여자
    withdrawal_date TIMESTAMP  -- 탈퇴 일시
);

-- ==========================
-- 로그인 기록 테이블
-- ==========================
CREATE TABLE login_history (
    history_id SERIAL PRIMARY KEY,  -- 로그인 기록 고유 번호
    member_id INTEGER NOT NULL REFERENCES members(user_no),  -- 로그인한 회원 번호 (외래키)
    login_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 로그인 일시
    logout_date TIMESTAMP,  -- 로그아웃 일시
    access_ip VARCHAR(45),  -- 접속 IP (IPv4/IPv6)
    access_device VARCHAR(200),  -- 접속 기기
    browser_info VARCHAR(300),  -- 브라우저 정보
    failure_reason VARCHAR(200)  -- 로그인 실패 사유
);

-- ==========================
-- 소셜 계정 테이블
-- ==========================
CREATE TABLE social_account (
    link_id SERIAL PRIMARY KEY,  -- 소셜 연동 고유 번호
    member_id INTEGER NOT NULL REFERENCES members(user_no),  -- 연동된 회원 번호 (외래키)
    social_platform VARCHAR(50) NOT NULL,  -- 소셜 플랫폼명 (Google, Facebook, Kakao, Naver)
    social_account_id VARCHAR(200) NOT NULL,  -- 소셜 플랫폼 계정 ID
    linked_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- 연동일시
    link_status CHAR(1) NOT NULL DEFAULT 'A',  -- 연동 상태 (A:활성, D:해제)
    token_info TEXT,  -- 리프레시 토큰 정보 (암호화 저장)
    profile_sync_flag BOOLEAN NOT NULL DEFAULT FALSE  -- 프로필 동기화 여부
);

-- ==========================
-- 데이터 수집 기록 테이블 (data_collection_history)
-- ==========================
CREATE TABLE data_collection_history (
    collection_id SERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL,
    collection_source VARCHAR(200) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    collected_count INTEGER DEFAULT 0,
    success_flag BOOLEAN NOT NULL DEFAULT TRUE,
    error_content TEXT,
    manager VARCHAR(50)
);

-- ==========================
-- 법령 테이블 (law)
-- ==========================
CREATE TABLE law (
    law_id SERIAL PRIMARY KEY,
    proclamation_date DATE NOT NULL,
    law_category_code VARCHAR(10) NOT NULL,
    law_name VARCHAR(500) NOT NULL,
    ministry_code VARCHAR(10) NOT NULL,
    enforcement_date DATE,
    revision_type VARCHAR(20),
    law_file_path TEXT
);

-- ==========================
-- 이슈 테이블 (issue)
-- ==========================
CREATE TABLE issue (
    issue_id SERIAL PRIMARY KEY,
    issue_name VARCHAR(200) NOT NULL,
    issue_description TEXT,
    keywords VARCHAR(500),
    occurrence_period TIMESTAMP,
    related_news_count INTEGER DEFAULT 0,
    news_sentiment REAL CHECK (news_sentiment >= 0 AND news_sentiment <= 1),
    sns_sentiment REAL CHECK (sns_sentiment >= 0 AND sns_sentiment <= 1),
    sentiment_total REAL CHECK (sentiment_total >= 0 AND sentiment_total <= 1),
    law_id INTEGER REFERENCES law(law_id) ON DELETE SET NULL,
    law_score REAL CHECK (law_score >= 0 AND law_score <= 1)
);

CREATE INDEX idx_issue_law ON issue(law_id);

-- ==========================
-- 뉴스 테이블 (news)
-- ==========================
CREATE TABLE news (
    news_id SERIAL PRIMARY KEY,  -- 뉴스 고유 식별번호
    title VARCHAR(500) NOT NULL,  -- 뉴스 제목
    news_content TEXT NOT NULL,  -- 뉴스 본문
    summary TEXT,  -- 뉴스 요약
    published_date TIMESTAMP NOT NULL,  -- 게시일자
    news_url VARCHAR(1000) NOT NULL,  -- 뉴스 원문 URL
    issue_id INTEGER REFERENCES issue(issue_id) ON DELETE SET NULL,  -- 관련 이슈
    collection_id INTEGER REFERENCES data_collection_history(collection_id) ON DELETE SET NULL  -- 수집 기록
);

CREATE INDEX idx_news_issue ON news(issue_id);
CREATE INDEX idx_news_collection ON news(collection_id);

-- ==========================
-- SNS 반응 테이블 (sns_reaction)
-- ==========================
CREATE TABLE sns_reaction (
    reaction_id SERIAL PRIMARY KEY,
    sns_platform VARCHAR(20) NOT NULL,
    post_content TEXT NOT NULL,
    created_date TIMESTAMP NOT NULL,
    sns_url VARCHAR(200),
    issue_id INTEGER REFERENCES issue(issue_id) ON DELETE SET NULL,
    collection_id INTEGER REFERENCES data_collection_history(collection_id) ON DELETE SET NULL
);

CREATE INDEX idx_sns_issue ON sns_reaction(issue_id);
CREATE INDEX idx_sns_collection ON sns_reaction(collection_id);

-- ==========================
-- 리포트 테이블 (report)
-- ==========================
CREATE TABLE report (
    report_id SERIAL PRIMARY KEY,
    issue_id INTEGER NOT NULL REFERENCES issue(issue_id) ON DELETE CASCADE,
    report_name VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_report_issue ON report(issue_id);

-- ==========================
-- 이슈-리포트 연결 테이블 (issue_report)
-- ==========================
CREATE TABLE issue_report (
    issue_report_id SERIAL PRIMARY KEY,
    issue_id INTEGER NOT NULL REFERENCES issue(issue_id) ON DELETE CASCADE,
    report_id INTEGER NOT NULL REFERENCES report(report_id) ON DELETE CASCADE
);

CREATE INDEX idx_issue_report_issue ON issue_report(issue_id);
CREATE INDEX idx_issue_report_report ON issue_report(report_id);