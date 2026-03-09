from pydantic import BaseModel
from agent.schema import LLMMessage


class NewSession(BaseModel):
    session_id: str

class SessionInfo(BaseModel):
    id: str
    name: str
    edited_at: str

class Sessionlist(BaseModel):
    sessions: list[SessionInfo]

class ChatResponse(BaseModel):
    message: LLMMessage
    session: SessionInfo

class ChatRequest(BaseModel):
    message: LLMMessage
    session: SessionInfo
    attachments: list[str] | None = None
