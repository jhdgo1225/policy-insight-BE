#!/bin/bash
set -e

echo "시작: Celery 워커 시작"

# 현재 디렉토리 표시
echo "현재 작업 디렉토리: $(pwd)"
echo "파일 목록:"
ls -la

# Celery 워커 시작
echo "Celery 워커 시작..."
celery -A celery_app worker --loglevel=info

echo "Celery 워커가 종료되었습니다."

# 프로세스 유지
wait