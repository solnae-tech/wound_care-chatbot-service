from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.result import router as result_router

app = FastAPI()

app.include_router(chat_router)
app.include_router(result_router)