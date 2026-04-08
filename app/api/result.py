from fastapi import APIRouter
from app.store.result_store import get_result

router = APIRouter()

@router.get("/result/{job_id}")
def get_chat_result(job_id: str):
    result = get_result(job_id)

    if result is not None:
        return result
    return {"status": "processing"}