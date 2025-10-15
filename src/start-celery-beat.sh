#!/bin/bash

# 현재 디렉토리를 기록
CURRENT_DIR=$(pwd)

# 스크립트 디렉토리로 이동
cd "$(dirname "$0")"

# Celery Beat 서비스 실행
echo "Celery Beat 스케줄러를 시작합니다..."
docker-compose -f celery-beat-compose.yml up -d

# 원래 디렉토리로 돌아가기
cd "$CURRENT_DIR"

echo "Celery Beat 스케줄러가 시작되었습니다."
echo "로그 확인: docker logs policy-insight-celery-beat"