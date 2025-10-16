import requests
import bs4
from bs4 import BeautifulSoup

# 필요한 모듈 임포트
from playwright.sync_api import sync_playwright, Page, Browser, Playwright
from datetime import datetime
import time
import re  # 정규표현식 사용을 위한 임포트

class NewsArticleCrawler(object):
	playwright = None
	browser = None
	page = None
	
	@classmethod
	def is_title_valid(cls, title):
		"""
		제목의 첫 부분이 [속보], [단독]으로 시작하는 경우와 
		대괄호로 시작하지 않는 경우만 유효한 것으로 판단
		
		유효한 제목:
		- [속보], [단독], [ 속보 ], [ 단독 ]로 시작하는 제목
		- 대괄호로 시작하지 않는 제목
		
		유효하지 않은 제목:
		- 위 두 조건이 아닌 [<텍스트>]로 시작하는 제목
		"""
		if not title:
			return False
			
		# 공백을 제거한 제목
		title_stripped = title.strip()
		
		# 대괄호로 시작하지 않는 경우 (유효)
		if not title_stripped.startswith('['):
			return True
			
		# [속보], [단독], [ 속보 ], [ 단독 ] 패턴 확인
		valid_prefixes = [
			r'^\[\s*속보\s*\]',
			r'^\[\s*단독\s*\]'
		]
		
		for pattern in valid_prefixes:
			if re.match(pattern, title_stripped):
				return True
				
		# 기타 [<텍스트>] 패턴 (유효하지 않음)
		return False

	@classmethod
	def __init_driver(cls):
		"""Playwright 초기화 (한 번만 실행)"""
		if cls.browser is None:
			cls.playwright = sync_playwright().start()
			cls.browser = cls.playwright.chromium.launch(
				headless=True,
			)
			cls.page = cls.browser.new_page(
				user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
			)

	@classmethod
	def __close_driver(cls):
		"""Playwright 종료"""
		if cls.page:
			cls.page.close()
			cls.page = None
		if cls.browser:
			cls.browser.close()
			cls.browser = None
		if cls.playwright:
			cls.playwright.stop()
			cls.playwright = None

	@classmethod
	def __get_soup(cls, url):
		html = requests.get(url)
		if html.status_code != 200:
			raise requests.exceptions.HTTPError()
		soup = BeautifulSoup(html.content, 'html.parser')
		return soup

	@classmethod
	def hankyung(cls, url):
		soup = cls.__get_soup(url)
		selector = soup.select("h1.headline")
		selector2 = soup.select("div.datetime > span.item > span.txt-date")
		selector3 = soup.select("div.article-body-wrap")
		# --- 제목 추출 ---
		title = ""
		if selector:  # 요소가 존재하는지 확인
			title = selector[0].text.strip()
			
			# 제목 필터링 - 유효하지 않은 제목이면 빈 문자열로 설정
			if not cls.is_title_valid(title):
				print(f"[한국경제] 필터링된 제목: {title}")
				return "", "", ""  # 빈 결과 반환
		else:
			print("[한국경제] h1.headline: 제목 요소가 아닙니다.")

		# --- 작성일자 추출 ---
		date = ""
		if selector2:  # 요소가 존재하는지 확인
			date = selector2[0].text
		else:
			print("[한국경제] div.datetime > span.item > span.txt-date: 작성일자 요소가 아닙니다.")

		# --- 본문 내용 추출 (텍스트 노드만 처리) ---
		content = ""
		if selector3:
			# div#articletxt 요소 찾기
			article_txt = selector3[0].find('div', id='articletxt')
			if article_txt:
				# 직접적인 자식 요소만 순회
				for child in article_txt.children:
					# NavigableString 타입인 경우(텍스트 노드)만 처리
					if isinstance(child, bs4.element.NavigableString):
					# 공백만 있는 텍스트는 건너뛰기
						text = child.strip()
						if text:  # 빈 텍스트가 아닌 경우만 content 변수에 연결
							content += f'{text}\n'
		else:
			print("[한국경제] div.article-body-wrap: 본문 요소가 아닙니다.")

		return title, date, content

	@classmethod
	def sekye(cls, url):
		soup = cls.__get_soup(url)
		selector = soup.select("section#contTitle > h3#title_sns")
		selector2 = soup.select("p.viewInfo")
		selector3 = soup.select("article.viewBox2")

		# --- 제목 추출 ---
		title = ""
		if selector:  # 요소가 존재하는지 확인
			title = selector[0].text.strip()
			
			# 제목 필터링 - 유효하지 않은 제목이면 빈 문자열로 설정
			if not cls.is_title_valid(title):
				print(f"[세계일보] 필터링된 제목: {title}")
				return "", "", ""  # 빈 결과 반환
		else:
			print("[세계일보] section#contTitle > h3#title_sns: 제목 요소가 아닙니다.")

		# --- 작성일자 추출 ---
		date_info = ""
		if selector2:  # 요소가 존재하는지 확인
			date_str = [child for child in selector2[0].children][0]
			pattern = r'입력\s*:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
			match = re.search(pattern, date_str)
			if match:
				date_info = match.group(1)
		else:
			print("[세계일보] p.viewInfo: 작성일자 요소가 아닙니다.")

		# --- 본문 내용 추출 (텍스트 노드만 처리) ---
		content = ""
		if selector3:
			# article.viewBox2 요소 내에서 모든 자식 요소 검색
			for child in selector3[0].find_all(recursive=True):
				# p 태그이면서 class 속성이 없는 요소만 선택
				if (child.name == 'p' and not child.get('class')):
					text = child.get_text(strip=True)
					if text:  # 빈 텍스트가 아닌 경우만 출력
						content += f'{text}\n'
		else:
			print("[세계일보] article.viewBox2: 본문 요소가 아닙니다.")

		return title, date_info, content

	@classmethod
	def chosun(cls, url):
		title = ""
		date = ""
		content = ""

		try:
			cls.__init_driver()

			# 페이지 로드
			cls.page.goto(url)

			# 페이지가 완전히 로드될 때까지 대기
			cls.page.wait_for_load_state("networkidle")

			# article-header__headline-container 클래스를 포함한 요소 찾기
			headline = cls.page.query_selector_all('h1.article-header__headline > span')

			if headline and len(headline) > 0:
				# 해당 요소 내에서 h1 태그 찾기
				title = headline[0].inner_text().strip()
				
				# 제목 필터링 - 유효하지 않은 제목이면 빈 문자열로 설정
				if not cls.is_title_valid(title):
					print(f"[조선일보] 필터링된 제목: {title}")
					return "", "", ""  # 빈 결과 반환
			else:
				print("[조선일보] h1.article-header__headline > span: 제목 요소가 아닙니다.")

			date_select = cls.page.query_selector_all('span.upDate')

			if date_select and len(date_select) > 0:
				date_text = date_select[0].inner_text()
				pattern3 = r'업데이트\s*(\d{4}.\d{2}.\d{2}.\s+\d{2}:\d{2})'
				match3 = re.search(pattern3, date_text)
				if match3:
					date = match3.group(1)
			else:
				print('[조선일보] span.upDate: 작성일자 요소가 아닙니다')

			paragraphs = cls.page.query_selector_all('p.article-body__content-text')
			if paragraphs and len(paragraphs) > 0:
				paragraph_texts = [paragraph.inner_text() for paragraph in paragraphs]
				content = "\n".join(paragraph_texts)
			else:
				print("[조선일보] p.article-body__content-text: 본문 요소가 아닙니다.")
			
		except Exception as e:
			print(f"[조선일보] Playwright 오류 발생: {e}")
		
		finally:
			# 브라우저 종료
			cls.__close_driver()
		return title, date, content
	
	@classmethod
	def joongang(cls, url):
		soup = cls.__get_soup(url)
		selector = soup.select("#container > section > article > header > h1")
		selector2 = soup.select("#container > section > article > header > div.datetime > div > p:nth-child(1) > time")
		selector3 = soup.select("#article_body > p")

		# --- 제목 추출 ---
		title = ""
		if selector:  # 요소가 존재하는지 확인
			title = selector[0].text.strip()
			
			# 제목 필터링 - 유효하지 않은 제목이면 빈 문자열로 설정
			if not cls.is_title_valid(title):
				print(f"[중앙일보] 필터링된 제목: {title}")
				return "", "", ""  # 빈 결과 반환
		else:
			print("[중앙일보] #container > section > article > header > h1: 제목 요소가 아닙니다.")

		# --- 작성일자 추출 ---
		date = ""
		if selector2:  # 요소가 존재하는지 확인
			date = datetime.fromisoformat(selector2[0].get('datetime')).strftime('%Y-%m-%d %H:%M:%S')
		else:
			print("[중앙일보] #container > section > article > header > div.datetime > div > p:nth-child(1) > time: 작성일자 요소가 아닙니다.")

		# --- 본문 내용 추출 (텍스트 노드만 처리) ---
		content = ""
		if selector3:
			# div#articletxt 요소 찾기
			for child in selector3:
				content += f"{child.get_text(strip=True)}\n"
		else:
			print("[중앙일보] #article_body > p: 본문 요소가 아닙니다.")

		return title, date, content

	@classmethod
	def munhwa(cls, url):
		soup = cls.__get_soup(url)
		selector = soup.select("header.article-header > h1.title")
		selector2 = soup.select("p.date-publish")
		selector3 = soup.select("p.text-l")
		# --- 제목 추출 ---
		title = ""
		if selector:  # 요소가 존재하는지 확인
			title = selector[0].text.strip()
			
			# 제목 필터링 - 유효하지 않은 제목이면 빈 문자열로 설정
			if not cls.is_title_valid(title):
				print(f"[문화일보] 필터링된 제목: {title}")
				return "", "", ""  # 빈 결과 반환
		else:
			print("[문화일보] header.article-header > h1.title: 제목 요소가 아닙니다.")

		# --- 작성일자 추출 ---
		if selector2:  # 요소가 존재하는지 확인
			date_string = selector2[0].text
			pattern3 = r'입력\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})'
			match3 = re.search(pattern3, date_string)
			if match3:
				date = match3.group(1)
		else:
			print("[문화일보] p.date-publish: 작성일자 요소가 아닙니다.")

		# --- 본문 내용 추출 (텍스트 노드만 처리) ---
		content = ""
		if selector3:
			# div#articletxt 요소 찾기
			for child in selector3:
				content += f"{child.get_text(strip=True)}\n"
		else:
			print("[문화일보] p.text-l: 본문 요소가 아닙니다.")

		return title, date, content
	
	@classmethod
	def crawl(cls, company, url):
		if (company == '한국경제'):
			return cls.hankyung(url)
		elif (company == '세계일보'):
			return cls.sekye(url)
		# ❗️ 보류...
		# elif (company == '조선일보'):
		# 	return cls.chosun(url)
		elif (company == '중앙일보'):
			return cls.joongang(url)
		elif (company == '문화일보'):
			return cls.munhwa(url)
		else:
			raise ValueError("You should request one of limited company => \n \
'한국경제', '세계일보', '중앙일보', '문화일보'")

if __name__ == "__main__":
	print("한국경제 뉴스기사 크롤링")
	print("====================================================================")
	title1, date1, content1 = NewsArticleCrawler.hankyung("https://www.hankyung.com/article/202510146992i")
	print(f"제목: {title1}")
	print(f"작성일자: {date1}")
	print(f"본문: {content1}")
	print()
	print("세계일보 뉴스기사 크롤링")
	print("====================================================================")
	title2, date2, content2 = NewsArticleCrawler.sekye("https://www.segye.com/newsView/20251013517372")
	print(f"제목: {title2}")
	print(f"작성일자: {date2}")
	print(f"본문: {content2}")
	print()
	# print("조선일보 뉴스기사 크롤링")
	# print("====================================================================")
	# title3, date3, content3 = NewsArticleCrawler.chosun("https://www.chosun.com/national/court_law/2025/10/13/B4TVCORIMNB6JB7UDALAUFJYTM/")
	# print(f"제목: {title3}")
	# print(f"작성일자: {date3}")
	# print(f"본문: {content3}")
	# print()
	print("중앙일보 뉴스기사 크롤링")
	print("====================================================================")
	title4, date4, content4 = NewsArticleCrawler.joongang("https://www.joongang.co.kr/article/25373503")
	print(f"제목: {title4}")
	print(f"작성일자: {date4}")
	print(f"본문: {content4}")
	print()
	print("문화일보 뉴스기사 크롤링")
	print("====================================================================")
	title5, date5, content5 = NewsArticleCrawler.munhwa("https://www.munhwa.com/article/11539048")
	print(f"제목: {title5}")
	print(f"작성일자: {date5}")
	print(f"본문: {content5}")