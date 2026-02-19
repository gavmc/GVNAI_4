from fastapi import APIRouter
from src.agent.schema import LLMMessage
from src.agent.agent import Agent


router = APIRouter(prefix="/chat")

@router.get("/", response_model=LLMMessage)
async def chat(request: LLMMessage):
    
    agent = Agent()

    # need to get chat history here

    response = await agent.run(
        messages=[request]
    )

    return response