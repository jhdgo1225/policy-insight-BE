FROM python:3.9-slim

# 시스템 타임존 설정 (한국 시간대로 설정)
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /code

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    dos2unix \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 필요한 Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 실행 파일 권한 문제 해결
RUN if [ -f /code/start-worker.sh ]; then \
    # 줄 바꿈 문자 수정 (Windows에서 편집한 경우)
    dos2unix /code/start-worker.sh || true; \
    # 실행 권한 설정 (더 관대하게)
    chmod +x /code/start-worker.sh; \
    # 소유자 설정
    chown root:root /code/start-worker.sh; \
    # 파일 존재 확인
    ls -la /code/start-worker.sh; \
  else \
    echo "ERROR: start-worker.sh 파일이 존재하지 않습니다!"; \
    exit 1; \
  fi

# start-celery-beat.sh 파일의 권한 설정
RUN if [ -f /code/start-celery-beat.sh ]; then \
    dos2unix /code/start-celery-beat.sh || true; \
    chmod +x /code/start-celery-beat.sh; \
    chown root:root /code/start-celery-beat.sh; \
    ls -la /code/start-celery-beat.sh; \
  fi

# 워커 시작
CMD ["sh", "-c", "/code/start-worker.sh"]