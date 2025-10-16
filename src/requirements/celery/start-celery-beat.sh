#!/bin/bash
set -e

echo "시작: Celery Beat 스케줄러 시작"

# 현재 디렉토리 표시
echo "현재 작업 디렉토리: $(pwd)"
echo "파일 목록:"
ls -la

# 스케줄 파일을 저장할 디렉토리 생성
mkdir -p /code/celerybeat
chmod 777 /code/celerybeat

echo "Celery Beat 스케줄러 시작..."

# 스케줄 파일 위치를 명시적으로 지정
echo "스케줄 파일 위치: /code/celerybeat/celerybeat-schedule"
celery -A celery_app beat --loglevel=info --schedule=/code/celerybeat/celerybeat-schedule

echo "Celery Beat가 종료되었습니다."

# 프로세스 유지
wait