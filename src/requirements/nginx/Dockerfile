FROM nginx:1.25-alpine

# SSL 인증서 생성을 위한 패키지 설치
RUN apk add --no-cache openssl

# SSL 인증서 생성
RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=Company/OU=Dev/CN=localhost"

RUN rm /etc/nginx/conf.d/default.conf
COPY ./conf/nginx.conf /etc/nginx/conf.d/