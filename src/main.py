from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes.chat import router as chat_router
from core.db import lifespan
from tools.registry import registry
from tools.builtin import TestTool, Sandbox

load_dotenv()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat")

registry.register(TestTool())
registry.register(Sandbox())

@app.get("/")
async def index():
    return {"running"}