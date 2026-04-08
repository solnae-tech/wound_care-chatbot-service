from fastapi import APIRouter
from app.store.result_store import get_result

router = APIRouter()

@router.get("/result/{task_id}")
def get_chat_result(task_id: str):
    result = get_result(task_id)

    if result:
        return result
    return {"status": "processing"}