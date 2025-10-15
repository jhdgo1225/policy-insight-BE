from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..tasks.sample_tasks import add, long_task, process_data
import uuid

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)

class AddTaskRequest(BaseModel):
    x: int
    y: int

class ProcessDataRequest(BaseModel):
    data: Dict[str, Any]

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None

# 태스크 상태를 저장할 인메모리 저장소 (실제로는 Redis나 DB를 사용하는 것이 좋음)
task_status = {}

@router.post("/add", response_model=TaskResponse)
async def run_add_task(request: AddTaskRequest):
    """
    두 숫자를 더하는 Celery 태스크를 실행합니다.
    """
    task = add.delay(request.x, request.y)
    task_status[task.id] = {"status": "PENDING", "type": "add"}
    return TaskResponse(
        task_id=task.id,
        status="PENDING",
        message=f"덧셈 태스크가 시작되었습니다. x={request.x}, y={request.y}"
    )

@router.post("/long-task", response_model=TaskResponse)
async def run_long_task():
    """
    오래 걸리는 Celery 태스크를 실행합니다.
    """
    task = long_task.delay()
    task_status[task.id] = {"status": "PENDING", "type": "long_task"}
    return TaskResponse(
        task_id=task.id,
        status="PENDING",
        message="오래 걸리는 태스크가 시작되었습니다."
    )

@router.post("/process-data", response_model=TaskResponse)
async def run_process_data_task(request: ProcessDataRequest):
    """
    데이터 처리 Celery 태스크를 실행합니다.
    """
    task = process_data.delay(request.data)
    task_status[task.id] = {"status": "PENDING", "type": "process_data"}
    return TaskResponse(
        task_id=task.id,
        status="PENDING",
        message="데이터 처리 태스크가 시작되었습니다."
    )

@router.get("/status/{task_id}", response_model=TaskResultResponse)
async def get_task_status(task_id: str):
    """
    Celery 태스크의 상태와 결과를 조회합니다.
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다.")
    
    task_type = task_status[task_id]["type"]
    
    if task_type == "add":
        task_result = add.AsyncResult(task_id)
    elif task_type == "long_task":
        task_result = long_task.AsyncResult(task_id)
    elif task_type == "process_data":
        task_result = process_data.AsyncResult(task_id)
    else:
        raise HTTPException(status_code=400, detail="알 수 없는 태스크 유형입니다.")
    
    response = TaskResultResponse(
        task_id=task_id,
        status=task_result.status
    )
    
    if task_result.ready():
        try:
            response.result = task_result.get()
        except Exception as e:
            response.status = "FAILURE"
            response.error = str(e)
    
    # 상태 업데이트
    task_status[task_id]["status"] = task_result.status
    
    return response