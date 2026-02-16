from tools.schema import ToolAction
from abc import ABC, abstractmethod
from typing import List, Dict, Any





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
    def actions(self) -> List[ToolAction]:
        ...

    @property
    @abstractmethod
    def active(self) -> bool:
        ...

    @property
    @abstractmethod
    def connection(self) -> bool:
        ...

    @property
    def formatted(self) -> List[Dict[str, Any]]:
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
        
    @property
    def summary_formatted(self) -> List[Dict[str, Any]]:
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
    def call_action(self, action: str, arguments: Dict[str, Any]) -> Any:
        ...



    




    