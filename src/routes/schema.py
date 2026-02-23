from pydantic import BaseModel
from agent.schema import LLMMessage
from typing import List

class ChatRequest(BaseModel):
    message: LLMMessage
    session_id: str

class NewSession(BaseModel):
    session_id: str

class SessionInfo(BaseModel):
    id: str
    name: str
    edited_at: str

class SessionList(BaseModel):
    sessions: List[SessionInfo]