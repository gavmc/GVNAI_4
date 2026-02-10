from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from enum import Enum


class ToolCategory(str, Enum):
    ACCOUNTING = "accounting"
    CRM = "crm"
    EMAIL = "email"
    CALENDAR = "calendar"
    ECOMMERCE = "ecommerce"
    PAYMENTS = "payments"
    DOCUMENTS = "documents"
    COMMUNICATION = "communication"
    SOCIAL_MEDIA = "social_media"
    TASKS = "tasks"
    ANALYTICS = "analytics"
    SCHEDULING = "scheduling"
    CUSTOM = "custom"

@dataclass
class ToolParameter:
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[str]] = None

@dataclass
class ToolAction:
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: str = "object"
    requires_confirmation: bool = False
    is_destructive: bool = False

@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_agent_message(self) -> str:
        if self.success:
            return f"Action succeeded. Result: {self.data}"
        return f"Action failed. Error: {self.error}"
    

class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @property
    @abstractmethod
    def category(self) -> ToolCategory:
        ...

    @property
    def is_connector(self) -> bool:
        return False
    
    @abstractmethod
    def get_actions(self) -> List[ToolAction]:
        ...

    @abstractmethod
    async def execute(self, action: str, params: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        ...

    
    def get_llm_schema(self) -> List[Dict[str, Any]]:
        
        functions = []
        for action in self.get_actions():
            properties = {}
            required = []
            for param in action.parameters:
                prop = {
                    "type": param.type,
                    "description": param.description,
                }

                if param.enum:
                    prop["enum"] = param.enum

                properties[param.name] = prop

                if param.required:
                    required.append(param.name)

            functions.append({
                "name": f"{self.name}__{action.name}",
                "description": f"[{self.display_name}] {action.description}",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
                "metadata": {
                    "tool": self.name,
                    "action": action.name,
                    "requires_confirmation": action.requires_confirmation,
                    "is_destructive": action.is_destructive,
                }
            })
        
        return functions



