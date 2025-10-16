import os
from celery import Celery
from dotenv import load_dotenv
from celery.signals import beat_init
from celery.schedules import crontab

# ============================================================
# 주의: 이 파일은 독립 Celery 서비스에서 사용됩니다.
# docker-compose에서 celery, celery-beat 서비스를 위해 사용됨
# 백엔드 애플리케이션의 Celery 설정과 별개입니다.
# ============================================================

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
    include=['scheduled_tasks']  # 태스크 모듈 경로
)

# Beat 초기화 시 태스크를 즉시 실행하기 위한 신호 핸들러
@beat_init.connect
def on_beat_init(sender, **kwargs):
    print("🚀 Celery Beat 초기화됨 - 초기 태스크 실행 중...")
    # scheduled_print 태스크 즉시 실행
    # sender.app.send_task('tasks.scheduled_print')
    # scheduled_crawling 태스크 즉시 실행
    sender.app.send_task('tasks.scheduled_crawling')
    print("✅ 초기 태스크 발송 완료")

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
    
    # 타임아웃 설정
    broker_transport_options={
        'visibility_timeout': 7200,  # 2시간 (RabbitMQ 메시지 가시성 타임아웃)
    },
    result_expires=86400,  # 결과 만료 시간 (24시간)
    
    # 작업 설정
    task_time_limit=2700,  # 작업 실행 시간 제한 (45분)
    task_soft_time_limit=2400,  # 작업 실행 소프트 제한 (40분, 경고 발생)
    
    # 추가 성능 설정
    task_acks_late=True,  # 작업 처리 후 승인
    task_reject_on_worker_lost=True,  # 워커가 죽으면 작업 거부
    
    # 워커 동시성 설정
    worker_concurrency=1,  # 워커 프로세스 수
    worker_max_tasks_per_child=1,  # 워커당 최대 작업 수 (메모리 누수 방지)
    
    # 작업 재시도 설정
    task_default_retry_delay=300,  # 재시도 전 5분 대기
    task_max_retries=3,  # 최대 3번 재시도
)

# 기본 태스크 설정
app.conf.task_default_queue = 'default'

# 스케줄링된 작업 설정
app.conf.beat_schedule = {
    # 1분 간격으로 실행되는 작업 (개발/테스트용)
    # (beat_init 신호 핸들러에 의해 시작 시에도 즉시 실행됨)
    # 'print-every-minute': {
    #     'task': 'tasks.scheduled_print',
    #     'schedule': 60.0,  # 60초 = 1분 간격
    # },
    # 1시간 간격으로 뉴스 크롤링 작업 실행
    # (beat_init 신호 핸들러에 의해 시작 시에도 즉시 실행됨)
    'news-crawling-hourly': {
        'task': 'tasks.scheduled_crawling',
        'schedule': 3600.0,  # 3600초(1시간) 간격
        'options': {
            'expires': 7200.0,  # 만료 시간 설정 (2시간)
            'time_limit': 2700,  # 시간 제한 (45분)
            'soft_time_limit': 2400,  # 소프트 시간 제한 (40분)
            'queue': 'crawling',  # 크롤링 전용 큐
        },
    },
}

if __name__ == '__main__':
    app.start()