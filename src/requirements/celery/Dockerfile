FROM python:3.9-slim

# 빌드 인자 정의 - worker 또는 beat
ARG SERVICE_TYPE=worker

# 서비스 타입 환경변수로 설정
ENV SERVICE_TYPE=${SERVICE_TYPE}

# 시스템 타임존 설정 (한국 시간대로 설정)
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Playwright 설정
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/ms-playwright
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING=UTF-8

WORKDIR /code

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    dos2unix \
    tzdata \
    wget \
    gnupg \
    curl \
    unzip \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Playwright 설치를 위한 환경 설정 (Chrome 대신)
ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/usr/local/ms-playwright \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=UTF-8

# 필요한 Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 설치 및 크로미움 브라우저 다운로드
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium

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

# 엔트리포인트 스크립트 추가
RUN echo '#!/bin/bash\necho "Starting Celery ${SERVICE_TYPE} service..."\necho "Playwright is installed with Chromium."\necho "Service Type: ${SERVICE_TYPE}"\necho "Executing command: $@"\nexec "$@"' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# 엔트리포인트 설정
ENTRYPOINT ["/entrypoint.sh"]

# 서비스 타입에 따라 시작 스크립트 선택
CMD ["sh", "-c", "if [ \"$SERVICE_TYPE\" = \"beat\" ]; then /code/start-celery-beat.sh; else /code/start-worker.sh; fi"]