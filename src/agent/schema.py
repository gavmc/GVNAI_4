from pydantic import BaseModel
from typing import Dict, Any, Literal, Optional, List


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]


class LLMMessage(BaseModel):
    role: Literal["user", "assistant", "tool", "system"]
    content: str = ""  
    thinking: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None # only for assistant
    tool_name: Optional[str] = None   # only for tool call