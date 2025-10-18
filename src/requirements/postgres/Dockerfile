FROM postgres:15.4-alpine

# 초기화 스크립트를 위한 디렉토리 생성
# RUN mkdir -p /docker-entrypoint-initdb.d

# 초기화 스크립트 복사 및 권한 설정
# COPY ./init/init.sql /docker-entrypoint-initdb.d/01-init.sql
# COPY ./init/sample_data.sql /docker-entrypoint-initdb.d/02-sample_data.sql

# RUN chmod 0755 /docker-entrypoint-initdb.d/*.sql

# PostgreSQL 데이터 디렉토리 생성 및 권한 설정
RUN mkdir -p /var/lib/postgresql/data && \
    chown -R postgres:postgres /var/lib/postgresql/data && \
    chmod 700 /var/lib/postgresql/data

USER postgres