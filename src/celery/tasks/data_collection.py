from celery import shared_task

@shared_task
def collect_data():
    pass  # 데이터 수집 로직 구현 예정