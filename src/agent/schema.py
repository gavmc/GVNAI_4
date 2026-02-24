from pydantic import BaseModel
from typing import Any, Literal


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]


class LLMMessage(BaseModel):
    role: Literal["user", "assistant", "tool", "system", "summary"]
    content: str = ""  
    thinking: str | None = None
    tool_calls: list[ToolCall] | None = None # only for assistant
    tool_name: str | None = None   # only for tool call