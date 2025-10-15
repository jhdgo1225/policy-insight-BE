import os
from celery import Celery
from dotenv import load_dotenv
from celery.schedules import crontab

# 환경 변수 로드
load_dotenv()

# Celery 설정
broker_url = os.environ.get('CELERY_BROKER_URL')
result_backend = os.environ.get('CELERY_RESULT_BACKEND')

# Celery 앱 인스턴스 생성
app = Celery(
    'tasks',
    broker=broker_url,
    backend=result_backend,
    include=['tasks', 'scheduled_tasks']  # 태스크 모듈 경로
)

# Celery 설정
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    
    # worker_prefetch_multiplier 설정 (global_qos 대신 사용)
    # 기본값 4에서 1로 변경하여 각 워커가 한 번에 하나의 메시지만 처리하도록 설정
    worker_prefetch_multiplier=1,
    
    # 추가 성능 설정
    task_acks_late=True,  # 작업 처리 후 승인
    task_reject_on_worker_lost=True,  # 워커가 죽으면 작업 거부
)

# 기본 태스크 설정
app.conf.task_default_queue = 'default'

# 스케줄링된 작업 설정
app.conf.beat_schedule = {
    # 1분 간격으로 실행되는 작업
    'print-every-minute': {
        'task': 'tasks.scheduled_print',
        'schedule': 60.0,  # 60초 = 1분 간격
    },
    # 매 시간 정각에 실행되는 작업 (예시)
    'print-every-hour': {
        'task': 'tasks.scheduled_print',
        'schedule': crontab(minute=0, hour='*'),  # 매 시간 정각
    },
}

if __name__ == '__main__':
    app.start()