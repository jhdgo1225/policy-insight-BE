#!/bin/bash

# 프로덕션 환경 배포 스크립트
docker-compose -f docker-compose.prod.yml up -d

# 마이그레이션 실행
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head