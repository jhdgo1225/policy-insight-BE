from app.tasks.celery_app import app
import time
from datetime import datetime
import pytz
import os
import platform
from tzlocal import get_localzone

@app.task(name='tasks.scheduled_task')
def scheduled_task():
    """
    1분마다 실행되는 스케줄된 태스크
    시스템의 로컬 타임존을 사용하여 현재 시간 표시
    """
    # 시스템의 로컬 타임존 가져오기
    try:
        local_tz = get_localzone()
    except Exception:
        # 타임존을 가져올 수 없는 경우 'Asia/Seoul' 사용
        local_tz = pytz.timezone('Asia/Seoul')
    
    # UTC 시간을 로컬 타임존으로 변환
    utc_now = datetime.now(pytz.utc)
    local_now = utc_now.astimezone(local_tz)
    
    # 시스템 정보 가져오기
    system_info = platform.system()
    timezone_name = local_tz.zone
    
    current_time = local_now.strftime("%Y-%m-%d %H:%M:%S")
    message = f"스케줄된 작업이 실행되었습니다. 현재 시간: {current_time} (시스템: {system_info}, 타임존: {timezone_name})"
    
    # 로그 출력 (Celery 워커 로그에 표시됨)
    print(message)
    
    # 결과 반환 (태스크 결과로 저장됨)
    return {
        "message": message,
        "timestamp": current_time,
        "timezone": timezone_name,
        "system": system_info,
        "execution_id": time.time()
    }