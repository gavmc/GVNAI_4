from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.agents.orchestrator import AgentOrchestrator
from app.api.deps import get_current_active_user
from app.models.models import User

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ToolCallResponse(BaseModel):
    tool: str
    params: dict
    result: dict | str | None
    success: bool

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tool_calls: list[ToolCallResponse] = []
    workflow_created: dict | None = None


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    conversation_id = UUID(request.conversation_id) if request.conversation_id else None

    agent = AgentOrchestrator(db, current_user.organization_id, current_user.id)

    response = agent.run(
        user_message=request.message,
        conversation_id=conversation_id,
    )

    return ChatResponse(
        response=response["response"],
        conversation_id=str(conversation_id),
        tool_calls=[ToolCallResponse(**tc) for tc in response.get("tool_calls", [])],
        workflow_created=response.get("workflow_created", False) # Update once workflows are a thing
    )




