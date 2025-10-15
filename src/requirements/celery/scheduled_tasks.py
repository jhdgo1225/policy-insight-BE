from celery_app import app
import time
from datetime import datetime

@app.task(name='tasks.scheduled_print')
def scheduled_print():
    """
    스케줄링된 태스크: 1분 간격으로 현재 시간을 출력
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"스케줄링된 작업 실행 - 현재 시간: {current_time}"
    print(message)
    return {"message": message, "timestamp": current_time}