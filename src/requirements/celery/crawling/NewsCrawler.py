from typing import List, Union, Optional, Dict, Any
from .company import companys
from .NewsArticleCrawler import NewsArticleCrawler
from .utils import parse_datetime, extract_text
from playwright.sync_api import sync_playwright, Page, Browser, Playwright
import datetime
from time import sleep
from datetime import datetime
import asyncio
import time

class NewsCrawler(object):
	"""각 인스턴스가 자체 Playwright 브라우저를 가지는 크롤러"""

	def __init__(self, company=None):
		"""생성자에서 Playwright 초기화"""
		self.playwright = None
		self.browser = None
		self.page = None
		self.company = company

	def _init_driver(self):
		"""Playwright 초기화 (인스턴스별로)"""
		if self.browser is None:
			try:
				print(f"[{self.company}] Playwright 초기화 시작...")
				self.playwright = sync_playwright().start()
				print(f"[{self.company}] Playwright 시작됨, 브라우저 실행 중...")
				
				# 타임아웃과 재시도 로직 추가
				retry_count = 0
				max_retries = 3
				
				while retry_count < max_retries:
					try:
						self.browser = self.playwright.chromium.launch(
							headless=True,
							timeout=30000,  # 30초 타임아웃
							args=[
								'--disable-gpu',
								'--disable-dev-shm-usage',
								'--disable-setuid-sandbox',
								'--no-sandbox',
								'--disable-extensions'
							]
						)
						break  # 성공하면 루프 탈출
					except Exception as e:
						retry_count += 1
						print(f"[{self.company}] 브라우저 시작 실패 ({retry_count}/{max_retries}): {str(e)}")
						if retry_count >= max_retries:
							raise  # 최대 재시도 횟수 초과시 예외 발생
						time.sleep(2)  # 잠시 대기 후 재시도
				
				print(f"[{self.company}] 브라우저 시작됨, 페이지 생성 중...")
				self.page = self.browser.new_page(
					user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
					viewport={'width': 1280, 'height': 800}
				)
				print(f"[{self.company}] Playwright 초기화 완료")
			except Exception as e:
				print(f"[{self.company}] Playwright 초기화 오류: {str(e)}")
				raise

	def _close_driver(self):
		"""Playwright 종료"""
		if self.page:
			self.page.close()
			self.page = None
		if self.browser:
			self.browser.close()
			self.browser = None
		if self.playwright:
			self.playwright.stop()
			self.playwright = None

	def _load_page(self, url: str, wait_selector: str = None):
		"""
		Playwright로 페이지 로드
		wait_selector: JavaScript 로딩 완료를 기다릴 요소의 CSS 선택자
		"""
		try:
			print(f"[{self.company}] 페이지 로드 시작: {url}")
			self._init_driver()
			
			# 페이지 로드 시도 (최대 5회 재시도)
			retry_count = 0
			max_retries = 5
			base_wait_time = 3  # 기본 대기 시간 (초)
			
			while retry_count < max_retries:
				try:
					# 요청 사이의 간격을 랜덤하게 조정 (레이트 리밋 방지)
					if retry_count > 0:
						# 재시도할 때마다 대기 시간 증가 (지수 백오프)
						wait_time = base_wait_time * (2 ** retry_count) + (time.time() % 3)
						print(f"[{self.company}] 재시도 {retry_count} - {wait_time:.1f}초 대기 후 요청...")
						time.sleep(wait_time)
					
					# 사용자 에이전트 랜덤 변경
					user_agents = [
						'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
						'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
						'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
						'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
					]
					if retry_count > 0:
						# 첫 시도 이후에만 새 컨텍스트 생성
						if self.page:
							self.page.close()
						
						import random
						new_agent = random.choice(user_agents)
						print(f"[{self.company}] 새 사용자 에이전트 사용: {new_agent[:20]}...")
						self.page = self.browser.new_page(
							user_agent=new_agent,
							viewport={'width': 1280, 'height': 800}
						)
					
					# 페이지 로드
					response = self.page.goto(url, timeout=45000, wait_until='domcontentloaded')
					
					if not response:
						print(f"[{self.company}] 응답을 받지 못했습니다: {url}")
						retry_count += 1
						continue
						
					status = response.status
					print(f"[{self.company}] 페이지 로드 응답 코드: {status}")
					
					# 429 에러 처리 (Too Many Requests)
					if status == 429:
						print(f"[{self.company}] ⚠️ 429 에러: 너무 많은 요청 - 더 긴 대기 시간 적용")
						retry_count += 1
						# 429 에러의 경우 더 긴 대기 시간 적용 (15-30초)
						wait_time = 15 + (retry_count * 5) + (time.time() % 5)
						print(f"[{self.company}] 레이트 리밋 대기: {wait_time:.1f}초...")
						time.sleep(wait_time)
						continue
					elif status >= 400:
						print(f"[{self.company}] 페이지 로드 실패 - HTTP 상태: {status}")
						retry_count += 1
						if retry_count >= max_retries:
							print(f"[{self.company}] 최대 재시도 횟수 초과: {url}")
							break
						time.sleep(base_wait_time * (retry_count + 1))  # 잠시 대기 후 재시도
						continue
					
					break  # 성공하면 루프 탈출
					
				except Exception as e:
					retry_count += 1
					print(f"[{self.company}] 페이지 로드 시도 {retry_count}/{max_retries} 실패: {str(e)}")
					if retry_count >= max_retries:
						print(f"[{self.company}] 페이지 로드 최대 재시도 횟수 초과: {url}")
						break
					time.sleep(2)  # 잠시 대기 후 재시도
			
			# 페이지가 완전히 로드될 때까지 기다림
			try:
				print(f"[{self.company}] 네트워크 요청 완료 대기 중...")
				self.page.wait_for_load_state("networkidle", timeout=15000)
				print(f"[{self.company}] 페이지 로드 완료: {url}")
			except Exception as e:
				print(f"[{self.company}] 네트워크 대기 시간 초과, 계속 진행합니다: {str(e)}")
			
			# JavaScript 동적 로딩 대기
			if wait_selector:
				try:
					print(f"[{self.company}] 선택자 대기 중: {wait_selector}")
					self.page.wait_for_selector(wait_selector, timeout=10000)
					sleep(1)  # 추가 안전 대기
					print(f"[{self.company}] 선택자 감지됨: {wait_selector}")
				except Exception as e:
					print(f"[{self.company}] 선택자 대기 중 에러 (무시하고 계속 진행): {str(e)}")
					
		except Exception as e:
			print(f"[{self.company}] 페이지 로드 과정에서 치명적 오류: {str(e)}")
			import traceback
			print(f"상세 오류: {traceback.format_exc()}")
			raise

	@staticmethod
	def crawl_sync(company: str) -> Optional[List[Dict[str, Any]]]:
		"""동기식 크롤링 메서드 - 각각의 회사마다 독립적인 인스턴스와 드라이버 사용"""
		print(f"[{company}] 크롤링 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
		crawler = NewsCrawler(company)  # 회사별로 독립된 크롤러 인스턴스 생성
		try:
			if not NewsCrawler.check_company(company):
				raise ValueError("You should request one of limited company => \n \
'한국경제', '세계일보', '중앙일보', '문화일보'")

			print(f"[{company}] 크롤러 인스턴스 생성 완료")
			result = []
			company_data = companys[company]
			domain = company_data.get('domain')
			items_count = company_data.get('items')
			# 셀렉터
			article_list_selector = company_data.get('article_list')
			categories = company_data.get('categories')
			print(f"[{company}] 설정 로드 완료: {len(categories)}개 카테고리, 도메인: {domain}")

			# 카테고리 요청 사이의 대기 시간을 랜덤하게 설정하기 위한 변수
			import random

			for category, info in categories.items():
				# 카테고리 간 랜덤 대기 시간 적용 (3-7초)
				category_wait = 3 + random.random() * 4
				print(f"[{company}] 카테고리 '{category}' 크롤링 시작 (대기 시간: {category_wait:.1f}초)")
				time.sleep(category_wait)

				for sub_category, sub_path in info['sub'].items():
					# 하위 카테고리 간 랜덤 대기 시간 적용 (1-3초)
					sub_category_wait = 1 + random.random() * 2
					print(f"[{company}] 하위 카테고리 '{sub_category}' 크롤링 시작 (대기 시간: {sub_category_wait:.1f}초)")
					time.sleep(sub_category_wait)
					
					page_no = 1 - (company == '세계일보')
					is_today = True

					while is_today:
						# 페이지 요청 전 잠시 대기 (1-2초)
						page_wait = 1 + random.random()
						time.sleep(page_wait)
						
						print(f"[{company}] {category}-{sub_category} 카테고리의 page={page_no}")
						page_url = f"{domain}{info['path']}{sub_path}?page={page_no}"
						for item_idx in range(items_count):
							# 페이지 로드 대기
							crawler._load_page(page_url)
							sleep(2)
							# 기사 목록 접근
							article_list_elements = crawler.page.query_selector_all(article_list_selector)

							if not article_list_elements:
								print(f"{page_url} 페이지의 CSS 셀렉터 - {article_list_selector} HTML 요소를 접근할 수 없습니다.")
								continue

							try:
								# 인덱스가 범위를 벗어나지 않는지 확인
								if item_idx < len(article_list_elements):
									item_element = article_list_elements[item_idx]
								else:
									print(f"인덱스 {item_idx}가 범위를 벗어납니다. 총 {len(article_list_elements)}개 항목이 있습니다.")
									continue
									
								# href 속성 가져오기
								href = item_element.get_attribute('href')

								if not href:
									print(f"No href found at index {item_element}")
									continue

								# 상대 경로 처리
								if href.startswith('/'):
									article_url = f"{domain}{href}"
								else:
									article_url = href

								print(f"Found article URL: {article_url}")
								
								# 기사 요청 간 랜덤 대기 시간 적용 (3-7초)
								import random
								article_wait = 3 + random.random() * 4
								print(f"[{company}] 기사 접근 전 {article_wait:.1f}초 대기...")
								sleep(article_wait)

								# ----------------------------------
								# 😀 여기서 NewsArticleCrawler 활용!
								# ----------------------------------
								title, date, content = NewsArticleCrawler.crawl(company, article_url)

								if (title == "" or date == "" or content == ""):
									continue

								# 날짜가 오늘인지 확인
								today = datetime.now().date()
								article_date = None

								# 문자열 형태의 날짜를 datetime 객체로 변환
								try:
									# date 문자열을 datetime 객체로 변환 (utils.parse_datetime 함수 활용)
									article_date = parse_datetime(date).date() if date else None
								except Exception as e:
									print(f"날짜 변환 중 오류: {e}")

								# 오늘 날짜가 아닌 경우 출력
								is_today = article_date == today if article_date else False
								if not is_today:
									print(f"⚠️ 오늘 날짜({today})가 아닌 기사입니다: {article_date}")
									break

								# 결과 객체에 추가
								article_data = {
									'title': title,
									'content': content,
									'category': category,
									'sub_category': sub_category,
									'published': date,
									'company': company,
									'news_url': article_url,
								}
								print(f"✅ 제목: {title}, 작성일자: {date}, 기사 URL: {article_url}")
								result.append(article_data)

							except Exception as e:
								print(f"기사 {page_url} 처리 중 에러: {e}")
								continue
						page_no += 1
			crawler._close_driver()
			return result

		except ValueError as v_err:
			print(v_err)
		except Exception as ex:
			print(f"크롤링 중 에러: {ex}")
		finally:
			# 드라이버 종료
			if (crawler):
				crawler._close_driver()

	@staticmethod
	def to_csv_sync(file_path: str, json_data: List[Dict[str, Any]]):
		"""동기식 CSV 작성 메서드"""
		import csv
		try:
			with open(file_path, mode='w', newline='', encoding="utf-8-sig") as file:
				writer = csv.writer(file)
				writer.writerow(['제목', '본문', '카테고리', '하위카테고리', '게시일자', '신문사', '기사링크'])
				for data in json_data:
					writer.writerow(
						[
							data['title'],
							data['content'],
							data['category'],
							data['sub_category'],
							data['published'],
							data['company'],
							data['news_url']
						]
					)
				print(f"{file_path} 작성 완료!!")
		except Exception as ex:
			print(f"{file_path} 작성 실패: {ex}")
	
	@staticmethod
	def check_company(company: str) -> bool:
		if company in companys:
			return True
		return False

class AsyncNewsCrawler:
    """회사별로 별도의 드라이버를 사용하는 비동기 크롤러"""
    
    @staticmethod
    async def crawl_company(company_name):
        """회사별 크롤링 작업을 비동기적으로 실행"""
        print(f"🚀 {company_name} 크롤링 시작...")
        
        try:
            # 비동기 작업을 이벤트 루프의 스레드 풀에서 실행
            # Playwright sync API는 비동기가 아니므로 run_in_executor로 별도 스레드에서 실행
            loop = asyncio.get_running_loop()
            
            print(f"⏳ {company_name}: 스레드 풀 작업 시작...")
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    lambda: NewsCrawler.crawl_sync(company_name)
                ),
                timeout=2700  # 45분 타임아웃 설정
            )
            print(f"✓ {company_name}: 스레드 풀 크롤링 작업 완료")
            
            if result:
                # CSV 작성도 스레드 풀에서 실행
                print(f"📝 {company_name}: CSV 파일 작성 시작...")
                await loop.run_in_executor(
                    None,
                    lambda: NewsCrawler.to_csv_sync(f"{company_name}.csv", result)
                )
                print(f"✅ {company_name} 크롤링 및 CSV 작성 완료!")
            else:
                print(f"⚠️ {company_name}: 크롤링 결과가 없거나 빈 결과입니다.")
        
            return result
            
        except asyncio.TimeoutError:
            print(f"⛔ {company_name}: 크롤링 작업 타임아웃 (45분 초과)")
            return None
        except Exception as e:
            import traceback
            print(f"❌ {company_name} 크롤링 중 예외 발생: {str(e)}")
            print(f"상세 오류: {traceback.format_exc()}")
            return None

async def crawl_all_company_articles():
    """모든 회사의 크롤링을 동시에 비동기적으로 실행"""
    print("\n==========================================================")
    print(f"📅 크롤링 작업 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==========================================================\n")
    
	# "조선일보", "중앙일보", "문화일보"
    companys_name = ["한국경제", "세계일보", "중앙일보", "문화일보"]
    print(f"크롤링 대상 회사: {', '.join(companys_name)}")
    
    start_time = time.time()
    
    try:
        # 각 회사별로 별도의 AsyncNewsCrawler 인스턴스로 비동기 실행
        # gather 대신 as_completed 사용하여 완료되는 순서대로 결과 수집
        tasks = {
            asyncio.create_task(AsyncNewsCrawler.crawl_company(company_name), name=company_name): company_name
            for company_name in companys_name
        }
        
        results = []
        task_list = list(tasks.keys())
        
        print(f"총 {len(task_list)}개 크롤링 작업 시작됨")
        
        # 최대 45분(2700초) 타임아웃 설정
        with_timeout = asyncio.wait_for(
            asyncio.gather(*task_list, return_exceptions=True),
            timeout=2700
        )
        
        all_results = await with_timeout
        
        # 결과 처리 및 로깅
        successful = 0
        for i, result in enumerate(all_results):
            company = companys_name[i]
            if isinstance(result, Exception):
                print(f"❌ {company} 크롤링 실패: {str(result)}")
            elif result:
                successful += 1
                print(f"✅ {company} 크롤링 성공 (기사 수: {len(result)})")
            else:
                print(f"⚠️ {company} 크롤링 결과 없음")
                
        results = all_results
    
    except asyncio.TimeoutError:
        print("⛔ 크롤링 전체 작업 시간 초과 (45분 초과)")
        results = []
    except Exception as e:
        import traceback
        print(f"❌ 크롤링 작업 중 예외 발생: {str(e)}")
        print(f"상세 오류: {traceback.format_exc()}")
        results = []

    # 작업 완료 로깅
    end_time = time.time()
    execution_time = end_time - start_time
    successful = sum(1 for r in results if r and not isinstance(r, Exception))

    print("\n==========================================================")
    print(f"🏁 크롤링 작업 완료 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 결과: 총 {len(companys_name)}개 회사 중 {successful}개 크롤링 성공")
    print(f"⏱️ 총 소요 시간: {execution_time:.2f}초")
    print("==========================================================\n")

    return results

if __name__ == '__main__':
    # 비동기 실행
    asyncio.run(crawl_all_company_articles())

