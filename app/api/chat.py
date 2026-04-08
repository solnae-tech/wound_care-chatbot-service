from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from app.queue.producer import send_task

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100, description="Unique user identifier")
    job_id: str = Field(..., min_length=1, max_length=100, description="Unique job identifier")
    wound_description: str = Field(..., min_length=1, max_length=500, description="Wound classifier output")
    pain_level: int = Field(..., ge=0, le=10, description="Pain level (0-10)")
    description: str = Field(..., min_length=1, max_length=1000, description="Patient symptom description")
    
    @field_validator('user_id', 'job_id', 'wound_description', 'description')
    @classmethod
    def validate_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v.strip()


@router.post("/chat")
def chat(request: ChatRequest):
    # Keep queue payload lean and aligned with async worker contract.
    payload = {
        "user_id": request.user_id,
        "job_id": request.job_id,
        "wound_description": request.wound_description,
        "pain_level": request.pain_level,
        "description": request.description,
    }
    
    job_id = send_task(payload)
    return {
        "job_id": job_id,
        "status": "processing"
    }