from playwright.async_api import async_playwright
import asyncio
import time
from datetime import datetime
import pytz
import os
import csv

class PlaywrightNewsCrawler:
    """Playwright를 사용하는 비동기 뉴스 크롤러"""

    @staticmethod
    async def crawl_company(company_name):
        """회사별 크롤링 작업을 비동기적으로 실행"""
        print(f"🚀 {company_name} 크롤링 시작...")
        
        try:
            result = []
            async with async_playwright() as p:
                # 브라우저 실행
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # 회사별 도메인 및 설정
                company_config = {
                    "한국경제": {
                        "domain": "https://www.hankyung.com",
                        "categories": ["경제", "정치"]
                    },
                    "세계일보": {
                        "domain": "https://www.segye.com",
                        "categories": ["경제", "정치"]
                    },
                    "조선일보": {
                        "domain": "https://www.chosun.com",
                        "categories": ["경제", "정치"]
                    },
                    "중앙일보": {
                        "domain": "https://www.joongang.co.kr",
                        "categories": ["경제", "정치"]
                    },
                    "문화일보": {
                        "domain": "https://www.munhwa.com",
                        "categories": ["경제", "정치"]
                    }
                }
                
                if company_name not in company_config:
                    print(f"⚠️ {company_name}에 대한 설정이 없습니다.")
                    return None
                
                config = company_config[company_name]
                domain = config["domain"]
                
                # 예시: 회사 메인 페이지 방문
                await page.goto(domain)
                await page.wait_for_load_state("networkidle")
                
                page_title = await page.title()
                print(f"📰 {company_name} 메인 페이지 제목: {page_title}")
                
                # 실제 크롤링 로직은 여기에 구현
                # 이 예시에서는 간단히 페이지 제목만 수집
                
                result.append({
                    "title": page_title,
                    "content": "크롤링 예시 콘텐츠",
                    "category": "예시",
                    "sub_category": "테스트",
                    "published": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "company": company_name,
                    "news_url": domain,
                })
                
                # 브라우저 종료
                await browser.close()
            
            # 결과가 있으면 CSV로 저장
            if result:
                await PlaywrightNewsCrawler.save_to_csv(f"{company_name}.csv", result)
                print(f"✅ {company_name} 크롤링 및 CSV 작성 완료!")
            
            return result
            
        except Exception as e:
            print(f"❌ {company_name} 크롤링 중 오류 발생: {str(e)}")
            return None

    @staticmethod
    async def save_to_csv(file_path, data):
        """결과를 CSV 파일로 저장"""
        try:
            with open(file_path, mode='w', newline='', encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(['제목', '본문', '카테고리', '하위카테고리', '게시일자', '신문사', '기사링크'])
                for item in data:
                    writer.writerow([
                        item.get('title', ''),
                        item.get('content', ''),
                        item.get('category', ''),
                        item.get('sub_category', ''),
                        item.get('published', ''),
                        item.get('company', ''),
                        item.get('news_url', '')
                    ])
                print(f"{file_path} 작성 완료!!")
        except Exception as ex:
            print(f"{file_path} 작성 실패: {ex}")

async def crawl_all_companies():
    """모든 회사의 크롤링을 동시에 비동기적으로 실행"""
    companies = ["한국경제", "세계일보", "조선일보", "중앙일보", "문화일보"]
    start_time = time.time()
    
    # 각 회사별로 별도로 비동기 실행
    tasks = [PlaywrightNewsCrawler.crawl_company(company) for company in companies]
    results = await asyncio.gather(*tasks)
    
    # 모든 작업이 완료되면
    end_time = time.time()
    successful = sum(1 for r in results if r)
    print(f"\n🏁 총 {len(companies)}개 회사 중 {successful}개 크롤링 완료!")
    print(f"✅ 총 소요 시간: {end_time - start_time:.2f}초")
    
    return {
        "successful_crawls": successful,
        "total_companies": len(companies),
        "execution_time_seconds": end_time - start_time
    }