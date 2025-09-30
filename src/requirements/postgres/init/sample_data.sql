-- ==========================
-- 샘플 데이터 삽입
-- ==========================

-- 회원 테이블 샘플 데이터
INSERT INTO members (email, passwd, user_name, profile_image, join_date, last_login, account_status, permission_level, permission_date, permission_granter) 
VALUES
    ('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyBAQ.TQAT/gAK', '관리자', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A', 'A', CURRENT_TIMESTAMP, 'System'),
    ('user1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyBAQ.TQAT/gAK', '홍길동', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A', 'U', CURRENT_TIMESTAMP, 'manager@example.com'),
    ('user2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyBAQ.TQAT/gAK', '김철수', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A', 'U', CURRENT_TIMESTAMP, 'manager@example.com');

-- 로그인 기록 샘플 데이터
INSERT INTO login_history (member_id, login_date, logout_date, access_ip, access_device, browser_info)
SELECT 
    m.user_no,
    CURRENT_TIMESTAMP - INTERVAL '1 day',
    CURRENT_TIMESTAMP - INTERVAL '23 hours',
    '192.168.1.100',
    'Windows 10',
    'Chrome 96.0.4664.110'
FROM members m WHERE m.email = 'admin@example.com'
UNION ALL
SELECT 
    m.user_no,
    CURRENT_TIMESTAMP - INTERVAL '2 days',
    CURRENT_TIMESTAMP - INTERVAL '1 day',
    '192.168.1.101',
    'MacOS',
    'Safari 15.0'
FROM members m WHERE m.email = 'user1@example.com'
UNION ALL
SELECT 
    m.user_no,
    CURRENT_TIMESTAMP - INTERVAL '12 hours',
    CURRENT_TIMESTAMP - INTERVAL '2 hours',
    '192.168.1.102',
    'iOS 15',
    'Mobile Safari'
FROM members m WHERE m.email = 'user2@example.com';

-- 소셜 계정 연동 샘플 데이터
INSERT INTO social_account (member_id, social_platform, social_account_id, link_status, profile_sync_flag)
SELECT 
    m.user_no,
    'Google',
    'google_user_123',
    'A',
    TRUE
FROM members m WHERE m.email = 'user2@example.com'
UNION ALL
SELECT 
    m.user_no,
    'Kakao',
    'kakao_user_456',
    'A',
    TRUE
FROM members m WHERE m.email = 'user2@example.com'
UNION ALL
SELECT 
    m.user_no,
    'Naver',
    'naver_user_789',
    'A',
    FALSE
FROM members m WHERE m.email = 'user2@example.com';

-- 법령 샘플 데이터
INSERT INTO law (proclamation_date, law_category_code, law_name, ministry_code, enforcement_date, revision_type)
VALUES
    ('2025-01-15', 'LAW001', '데이터 산업진흥법', 'GOV001', '2025-07-01', '제정'),
    ('2025-02-20', 'LAW002', '인공지능 윤리기준', 'GOV002', '2025-08-01', '제정'),
    ('2025-03-10', 'LAW003', '디지털 플랫폼 공정화에 관한 법률', 'GOV003', '2025-09-01', '개정');

-- 이슈 샘플 데이터
INSERT INTO issue (issue_name, issue_description, keywords, occurrence_period, related_news_count, news_sentiment, sns_sentiment, sentiment_total, law_id, law_score)
VALUES
    ('AI 윤리규제 도입', 'AI 윤리규제 법안 도입에 따른 산업계 영향', 'AI,윤리,규제,산업', CURRENT_TIMESTAMP, 150, 0.75, 0.68, 0.72, 2, 0.85),
    ('데이터 거래소 출범', '데이터 거래소 출범으로 인한 데이터 경제 활성화', '데이터,거래소,경제', CURRENT_TIMESTAMP, 200, 0.82, 0.79, 0.81, 1, 0.90),
    ('플랫폼 규제 강화', '디지털 플랫폼 규제 강화에 따른 시장 변화', '플랫폼,규제,공정화', CURRENT_TIMESTAMP, 180, 0.65, 0.58, 0.62, 3, 0.78);

-- 뉴스 샘플 데이터
INSERT INTO news (title, news_content, summary, published_date, news_url, issue_id)
VALUES
    ('AI 윤리규제 법안 국회 통과', 'AI 윤리규제에 관한 법안이 국회 본회의를 통과했다...', 'AI 윤리규제 법안 통과로 인한 산업계 영향 예상', CURRENT_TIMESTAMP - INTERVAL '2 days', 'https://news.example.com/article1', 1),
    ('데이터 거래소 첫 거래액 100억 돌파', '데이터 거래소 출범 이후 첫 거래액이 100억을 돌파했다...', '데이터 거래소 성공적 출범', CURRENT_TIMESTAMP - INTERVAL '1 day', 'https://news.example.com/article2', 2),
    ('플랫폼 기업 규제 강화 반발', '디지털 플랫폼 기업들이 새로운 규제에 반발하고 있다...', '플랫폼 기업 규제 강화에 대한 반발', CURRENT_TIMESTAMP, 'https://news.example.com/article3', 3);

-- SNS 반응 샘플 데이터
DO $$ 
DECLARE
    ai_issue_id INTEGER;
    data_issue_id INTEGER;
    platform_issue_id INTEGER;
BEGIN
    SELECT issue_id INTO ai_issue_id FROM issue WHERE issue_name = 'AI 윤리규제 도입';
    SELECT issue_id INTO data_issue_id FROM issue WHERE issue_name = '데이터 거래소 출범';
    SELECT issue_id INTO platform_issue_id FROM issue WHERE issue_name = '플랫폼 규제 강화';

    INSERT INTO sns_reaction (sns_platform, post_content, created_date, sns_url, issue_id)
    VALUES
        ('Twitter', 'AI 윤리규제는 혁신을 저해할 수 있습니다. #AI규제', CURRENT_TIMESTAMP - INTERVAL '1 day', 'https://t.co/abc123', ai_issue_id),
        ('Facebook', '데이터 거래소 출범으로 데이터 경제가 활성화될 것으로 기대됩니다.', CURRENT_TIMESTAMP - INTERVAL '12 hours', 'https://fb.com/xyz789', data_issue_id),
        ('Instagram', '플랫폼 규제, 소비자 보호를 위해 필요한 조치입니다. #플랫폼규제', CURRENT_TIMESTAMP - INTERVAL '6 hours', 'https://ig.com/pqr456', platform_issue_id);
END $$;

-- 리포트 샘플 데이터
WITH report_data AS (
    INSERT INTO report (issue_id, report_name, report_type, created_date)
    SELECT 
        i.issue_id,
        d.report_name,
        d.report_type,
        d.created_date
    FROM (
        VALUES 
            ('AI 윤리규제 도입', 'AI 윤리규제 영향 분석 보고서', '영향분석', CURRENT_TIMESTAMP - INTERVAL '1 day'),
            ('데이터 거래소 출범', '데이터 거래소 시장 전망', '시장분석', CURRENT_TIMESTAMP - INTERVAL '2 days'),
            ('플랫폼 규제 강화', '플랫폼 규제 정책 리포트', '정책분석', CURRENT_TIMESTAMP - INTERVAL '3 days')
    ) AS d(issue_name, report_name, report_type, created_date)
    JOIN issue i ON i.issue_name = d.issue_name
    RETURNING issue_id, report_id
)
-- 이슈-리포트 연결 샘플 데이터
INSERT INTO issue_report (issue_id, report_id)
SELECT issue_id, report_id FROM report_data;