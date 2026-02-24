from agent.schema import LLMMessage
from models.message import Message
from models.session import Session
from routes.schema import SessionInfo
from agent.summarizer import Summarizer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from uuid import UUID
from datetime import datetime, timezone


async def save_message(session_id: UUID, message: LLMMessage, db: AsyncSession):
    
    current_session = await db.get(Session, session_id)

    if not current_session:
        raise ValueError(f"Session does not exist: {session_id}")
    
    current_message = Message(message=message.model_dump())
    current_message.session = current_session
    current_session.edited_at = datetime.now(timezone.utc)

    db.add(current_message)
    await db.commit()
    await db.refresh(current_message)
    


async def get_history(session_id: UUID, db: AsyncSession) -> list[LLMMessage]:

    result = await db.execute(Select(Message).where(Message.session_id == session_id).order_by(Message.id))
    messages = result.scalars().all()

    return [LLMMessage(**msg.message) for msg in messages]


async def create_session(db: AsyncSession, name: str | None = None) -> Session:

    session = Session()
    if name:
        session.name = name

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session


async def get_sessions(db: AsyncSession) -> list[SessionInfo]:

    result = await db.execute(Select(Session).order_by(Session.edited_at))

    sessions = result.scalars().all()

    return [SessionInfo(id=str(session.id), name=session.name, edited_at=str(session.edited_at)) for session in sessions]


async def get_summary(message: LLMMessage) -> LLMMessage:
    sum = Summarizer()
    return await sum.run([message])