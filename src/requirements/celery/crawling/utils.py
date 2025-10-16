from typing import List
import re
from datetime import datetime

def extract_text(element, all_texts):
    """
    재귀적 텍스트 추출
    """
    if element.text and element.text.strip():
        all_texts.append(element.text.strip())
    for child in element:
        extract_text(child, all_texts)
    if element.tail and element.tail.strip():
        all_texts.append(element.tail.strip())

def datetime_string_to_date(datetime_string: str) -> List[int]:
    """
    문자열에서 숫자만 추출하여 연도, 월, 일, 시, 분, 초 형태로 반환합니다.
    
    방법 1: 정규표현식 사용
    """
    # 정규표현식으로 숫자 그룹 추출
    numbers = re.findall(r'\d+', datetime_string)
    
    # 숫자를 정수로 변환
    return [int(num) for num in numbers]


def datetime_string_to_date_alt(datetime_string: str) -> List[int]:
    """
    문자열에서 숫자만 추출하여 연도, 월, 일, 시, 분, 초 형태로 반환합니다.
    
    방법 2: 문자 분할 후 숫자만 필터링
    """
    result = []
    current_number = ''
    
    for char in datetime_string:
        if char.isdigit():
            current_number += char
        elif current_number:
            result.append(int(current_number))
            current_number = ''
            
    # 마지막 숫자가 있으면 추가
    if current_number:
        result.append(int(current_number))
        
    return result


def parse_datetime(datetime_string: str) -> datetime:
    """
    날짜 문자열을 파싱하여 datetime 객체로 변환합니다.
    여러 형식을 지원하도록 구현할 수 있습니다.
    """
    # 여러 가능한 형식들
    formats = [
        "%Y. %m. %d %H:%M",
        "%Y.%m.%d %H:%M",
        "%Y-%m-%d %H:%M",
        "%Y.%m.%d. %H:%M",
		"%Y-%m-%d %H:%M:%S",
		"%Y.%m.%d %H:%M:%S",
        "%Y. %m. %d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(datetime_string, fmt)
        except ValueError:
            continue

    return datetime.now()


if __name__ == "__main__":
    dt = parse_datetime("2025.05.23. 12:34")
    dt_now = datetime.now().date()
    if dt:
        print(f"변환된 날짜: {dt.date()}")
        print(f"오늘 날짜: {dt_now}")
        print(f"포맷팅된 날짜: {dt.strftime('%Y년 %m월 %d일 %H시 %M분')}")