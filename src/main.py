from fastapi import FastAPI
from dotenv import load_dotenv
from routes.chat import router as chat_router
from db import lifespan
from tools.registry import registry
from tools.builtin.test_tool import TestTool

load_dotenv()

app = FastAPI(lifespan=lifespan)

app.include_router(chat_router, prefix="/chat")

registry.register(TestTool())

@app.get("/")
async def index():
    return {"running"}