from .celery_app import app
from .sample_tasks import add, long_task, process_data

# 모든 태스크를 이 모듈에서 접근할 수 있도록 노출
# 이렇게 하면 'from tasks import add' 형태로 임포트 가능

# 샘플 태스크 노출
add = add
long_task = long_task
process_data = process_data