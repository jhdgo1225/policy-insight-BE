from celery import Celery
import os
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
    include=[
        'app.tasks.sample_tasks',  # 샘플 태스크 모듈
        'app.tasks.scheduled_tasks',  # 스케줄링된 태스크 모듈
        # 다른 태스크 모듈 추가
    ]
)

# Celery 설정
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
)

# 스케줄링 설정
app.conf.beat_schedule = {
    'run-every-minute': {
        'task': 'tasks.scheduled_task',
        'schedule': 60.0,  # 60초(1분) 간격
        'args': (),
        'options': {
            'expires': 59.0,  # 만료 시간 설정 (다음 스케줄이 시작되기 전에 작업이 만료되도록)
        },
    },
    # 추가 스케줄된 작업이 필요하면 여기에 추가
}

# 기본 태스크 설정
app.conf.task_default_queue = 'default'