from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID
from agent.schema import LLMMessage
from agent.agent import Agent
from utils import get_history, save_message, create_session
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class ChatRequest(BaseModel):
    message: LLMMessage
    session_id: str

class NewSession(BaseModel):
    session_id: str


@router.post("/", response_model=LLMMessage)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    
    #47204ed9-aea7-4bc2-8e89-cd93a0469cba

    agent = Agent()

    history = await get_history(UUID(request.session_id), db)
    history.append(request.message)

    await save_message(UUID(request.session_id), request.message, db)


    response = await agent.run(
        messages=history,
    )

    await save_message(UUID(request.session_id), response, db)

    return response



@router.post('/new', response_model=NewSession)
async def new(db: AsyncSession = Depends(get_db)):
    
    session_id = await create_session(db)

    return NewSession(session_id=str(session_id))