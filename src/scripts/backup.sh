#!/bin/bash

# 데이터베이스 백업
docker-compose exec postgresql /backup/backup.sh

# 백업 파일을 외부 저장소로 복사
# AWS S3나 다른 백업 저장소로의 복사 로직 추가 예정