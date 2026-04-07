from fastapi import APIRouter
from app.core.chatbot import chatbot

router = APIRouter()

@router.post("/chat")
def chat(payload: dict):
    return chatbot(payload)