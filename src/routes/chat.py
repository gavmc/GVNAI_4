from fastapi import APIRouter, Depends
from uuid import UUID
from agent.schema import LLMMessage
from agent.agent import Agent
from routes.schema import ChatRequest, Sessionlist, ChatResponse, SessionInfo
from utils import get_history, save_messages, get_sessions, get_summary, create_session
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    
    agent = Agent()
    name = None
    session = None

    history = await get_history(UUID(request.session.id), db)

    if not history:
        name = await get_summary(request.message)
        session = await create_session(db, name.content)
        session_id = str(session.id)

    else:
        session_id = request.session.id

    history.append(request.message)

    response = await agent.run(
        messages=history,
    )

    await save_messages(UUID(session_id), [request.message, *response], db)

    if session:
        return ChatResponse(
            message=response[-1],
            session=SessionInfo(
                id=str(session.id),
                name=session.name,
                edited_at=str(session.edited_at),
            )
        )

    return ChatResponse(
        message=response[-1],
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
