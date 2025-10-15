from .celery_app import app
import time

@app.task(name='tasks.add')
def add(x, y):
    """
    샘플 태스크: 두 숫자를 더함
    """
    return x + y

@app.task(name='tasks.long_task')
def long_task():
    """
    샘플 태스크: 오래 걸리는 작업 시뮬레이션
    """
    time.sleep(5)
    return {'status': 'completed'}

@app.task(name='tasks.process_data')
def process_data(data):
    """
    샘플 태스크: 데이터 처리
    """
    result = {"processed": data}
    return result