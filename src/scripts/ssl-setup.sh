#!/bin/bash

# SSL 인증서 갱신
certbot renew

# 인증서 갱신 후 Nginx 재시작
docker-compose restart nginx