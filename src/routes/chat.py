from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import UUID
from typing import List
from agent.schema import LLMMessage
from agent.agent import Agent
from routes.schema import ChatRequest, NewSession, SessionInfo, SessionList
from utils import get_history, save_message, create_session, get_sessions
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/", response_model=LLMMessage)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    
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


@router.get('/sessions', response_model=SessionList)
async def sessions(db: AsyncSession = Depends(get_db)):

    return SessionList(
        sessions = await get_sessions(db)
    )

@router.get('/history/{session_id}', response_model=List[LLMMessage])
async def chat_history(session_id: str, db: AsyncSession = Depends(get_db)):
    return await get_history(UUID(session_id), db)