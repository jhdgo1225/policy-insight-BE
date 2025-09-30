.PHONY: build up down logs clean-all clean-volumes clean-images

build:
	docker-compose -f src/docker-compose.yml build

up:
	docker-compose -f src/docker-compose.yml up -d

down:
	docker-compose -f src/docker-compose.yml down

logs:
	docker-compose -f src/docker-compose.yml logs -f

# 컨테이너, 네트워크, 볼륨 삭제
clean-volumes:
	docker-compose -f src/docker-compose.yml down -v

# 특정 프로젝트의 이미지만 삭제
clean-images:
	docker rmi policy-insight-nginx policy-insight-backend policy-insight-postgresql

# 컨테이너, 네트워크, 볼륨, 이미지 모두 삭제 (주의: 모든 중지된 컨테이너와 미사용 이미지가 삭제됨)
clean-all:
	docker-compose -f src/docker-compose.yml down -v
	docker rmi policy-insight-nginx policy-insight-backend policy-insight-postgresql
