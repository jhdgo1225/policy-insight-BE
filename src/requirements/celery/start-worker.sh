#!/bin/bash
set -e

echo "시작: Celery 워커와 Flower 모니터링 시작"

# 현재 디렉토리 표시
echo "현재 작업 디렉토리: $(pwd)"
echo "파일 목록:"
ls -la

# Celery 워커 시작
echo "Celery 워커 시작..."
celery -A celery_app worker --loglevel=info &
WORKER_PID=$!
echo "Celery 워커 시작됨 (PID: $WORKER_PID)"

echo "Celery Beat 스케줄러 시작..."

# 스케줄 파일을 저장할 디렉토리 생성
mkdir -p /code/celerybeat
chmod 777 /code/celerybeat

# 현재 디렉토리 표시
echo "현재 작업 디렉토리: $(pwd)"
echo "파일 목록:"
ls -la /code

# Celery Beat 시작
# 스케줄 파일 위치를 명시적으로 지정
echo "스케줄 파일 위치: /code/celerybeat/celerybeat-schedule"
celery -A celery_app beat --loglevel=info --schedule=/code/celerybeat/celerybeat-schedule

echo "Celery Beat가 종료되었습니다."

# Flower 모니터링 시작 (옵션)
echo "Flower 모니터링 시작..."
celery -A celery_app flower --port=5555 &
FLOWER_PID=$!
echo "Flower 모니터링 시작됨 (PID: $FLOWER_PID)"

echo "모든 서비스가 시작되었습니다."

# 프로세스 유지
wait