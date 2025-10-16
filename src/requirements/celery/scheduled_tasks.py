from celery_app import app
import time
from datetime import datetime
import asyncio
import pytz
from tzlocal import get_localzone
import sys
import os
from crawling.NewsCrawler import crawl_all_company_articles

@app.task(name='tasks.scheduled_crawling')
def scheduled_crawling():
    """
    1시간마다 실행되는 뉴스 크롤링 태스크
    모든 회사의 크롤링을 비동기적으로 실행
    """
    # 현재 시간 기록
    start_time = time.time()
    
    # 시스템의 로컬 타임존 가져오기
    try:
        local_tz = get_localzone()
    except Exception:
        # 타임존을 가져올 수 없는 경우 'Asia/Seoul' 사용
        local_tz = pytz.timezone('Asia/Seoul')
    
    # 현재 시간 표시
    utc_now = datetime.now(pytz.utc)
    local_now = utc_now.astimezone(local_tz)
    current_time = local_now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"📅 뉴스 크롤링 작업 시작 - {current_time}")
    
    try:
        print("환경 설정 확인...")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        print(f"파일 목록: {os.listdir('.')}")
        print(f"크롤링 디렉토리 확인: {os.listdir('./crawling') if os.path.exists('./crawling') else '크롤링 디렉토리 없음'}")
        
        print("🚀 NewsCrawler를 사용한 비동기 크롤링 시작...")
        
        # asyncio.run은 기존 이벤트 루프가 있으면 에러가 발생하므로 직접 루프를 관리
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # NewsCrawler를 사용한 크롤링 실행
        try:
            print("크롤링 작업 시작 중...")
            results = loop.run_until_complete(crawl_all_company_articles())
            print("크롤링 작업 완료")
        finally:
            # 항상 이벤트 루프를 닫아줍니다
            try:
                loop.close()
                print("이벤트 루프 종료됨")
            except Exception as e:
                print(f"이벤트 루프 종료 중 오류: {e}")
        
        # 성공적으로 크롤링된 회사 수 계산
        successful_crawls = sum(1 for r in results if r and not isinstance(r, Exception))
        total_companies = len(["한국경제", "세계일보", "중앙일보", "문화일보"])  # 크롤링 대상 회사 수
        execution_time = time.time() - start_time
        
        # 결과 출력
        print(f"\n🏁 총 {total_companies}개 회사 중 {successful_crawls}개 크롤링 완료!")
        print(f"✅ 총 소요 시간: {execution_time:.2f}초")
        
        # 결과 반환
        return {
            "message": f"뉴스 크롤링 작업 완료: {successful_crawls}/{total_companies}개 회사",
            "timestamp": current_time,
            "execution_time_seconds": execution_time,
            "successful_crawls": successful_crawls
        }
    except Exception as e:
        import traceback
        print(f"크롤링 작업 중 오류 발생: {e}")
        print(f"상세 오류: {traceback.format_exc()}")
        return {
            "message": f"크롤링 작업 실패: {str(e)}",
            "timestamp": current_time,
            "execution_time_seconds": time.time() - start_time,
            "successful_crawls": 0
        }