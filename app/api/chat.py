from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.queue.producer import send_task

router = APIRouter()


class DLOutput(BaseModel):
    infection_detected: bool = False


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    pain_level: int = Field(..., ge=0, le=10, description="Pain level (0-10)")
    discomfort_level: int = Field(..., ge=0, le=10, description="Discomfort level (0-10)")
    dl_output: Optional[DLOutput] = Field(default_factory=lambda: DLOutput())
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()


@router.post("/chat")
def chat(request: ChatRequest):
    # Convert to dict for processing
    payload = {
        "message": request.message,
        "pain_level": request.pain_level,
        "discomfort_level": request.discomfort_level,
        "dl_output": request.dl_output.model_dump()
    }
    
    task_id = send_task(payload)
    return {
        "task_id": task_id,
        "status": "processing"
    }