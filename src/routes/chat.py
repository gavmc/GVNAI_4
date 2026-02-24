from fastapi import APIRouter, Depends
from uuid import UUID
from agent.schema import LLMMessage
from agent.agent import Agent
from routes.schema import ChatRequest, Sessionlist, ChatResponse, SessionInfo
from utils import get_history, save_message, get_sessions, get_summary, create_session
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    
    agent = Agent()
    name = None

    history = await get_history(UUID(request.session.id), db)

    if not history:
        name = await get_summary(request.message)
        session = await create_session(db, name)

    history.append(request.message)

    await save_message(UUID(request.session_id), request.message, db)


    response = await agent.run(
        messages=history,
    )

    await save_message(UUID(request.session_id), response, db)

    if session:
        return ChatResponse(
            message=response,
            session=SessionInfo(
                id=session.id,
                name=session.name,
                edited_at=session.edited_at,
            )
        )

    return ChatResponse(
        message=response,
        session=request.session,
    )


@router.get('/sessions', response_model=Sessionlist)
async def sessions(db: AsyncSession = Depends(get_db)):

    return Sessionlist(
        sessions = await get_sessions(db)
    )

@router.get('/history/{session_id}', response_model=list[LLMMessage])
async def chat_history(session_id: str, db: AsyncSession = Depends(get_db)):
    return await get_history(UUID(session_id), db)
