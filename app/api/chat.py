from fastapi import APIRouter
from app.queue.producer import send_task

router = APIRouter()

@router.post("/chat")
def chat(payload: dict):
    task_id = send_task(payload)
    return {
        "task_id": task_id,
        "status": "processing"
    }