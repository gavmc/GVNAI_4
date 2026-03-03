from tools.schema import ToolAction
from abc import ABC, abstractmethod
from typing import Any


class Base(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @property
    @abstractmethod
    def actions(self) -> list[ToolAction]:
        ...

    @property
    @abstractmethod
    def active(self) -> bool:
        ...

    @property
    @abstractmethod
    def connection(self) -> bool:
        ...

    def formatted(self) -> list[dict[str, Any]]:
        actions = self.actions
        func_def = []

        if not actions:
            return []

        for action in actions:
            current = {
                "type": "function",
                "function": {
                    "name": f"{self.name}__{action.name}",
                    "description": action.description,
                    "parameters": {
                        "type": action.type,
                        "required": [param.name for param in action.parameters if param.required],
                        "properties": {
                            param.name: {
                                "type": param.type,
                                "description": param.description,
                                "enum": param.enum,
                            }
                        for param in action.parameters} 
                    }
                }
            }

            func_def.append(current)

        return func_def
        
    def summary_formatted(self) -> list[dict[str, Any]]:
        actions = self.actions
        func_def = []

        if not actions:
            return []

        for action in actions:
            current = {
                "name": f"{self.name}__{action.name}",
                "description": self.description,
            }

            func_def.append(current)

        return func_def
    

    @abstractmethod
    async def call_action(self, action: str, arguments: dict[str, Any]) -> Any:
        ...



    




    