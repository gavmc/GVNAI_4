from tools.schema import ToolAction, ToolParameter
from tools.base import Base
from typing import Any


class TestTool(Base):
    def __init__(self):
        pass
    
    @property
    def name(self) -> str:
        return "user_name"
    
    @property
    def description(self) -> str:
        return "Returns users name as a string"
    
    @property
    def actions(self) -> list[ToolAction]:
        return [
            ToolAction(
                name="get_first_name",
                description=" Returns users first name",
                parameters=[ToolParameter(
                    name="last_name",
                    type="string",
                    description="The user's last name",
                    required=True
                )],
                type="object"
            ),
            ToolAction(
                name="get_last_name",
                description=" Returns users last name",
                parameters=[],
                type="object"
            )
        ]
    
    @property
    def active(self) -> bool:
        return True
    
    @property
    def connection(self) -> bool:
        return True

    async def call_action(self, action: str, arguments: dict[str, Any]) -> Any:

        try:
            if action == "get_first_name":
                return self._get_first_name(**arguments)
            if action == "get_last_name":
                return self._get_last_name(**arguments)

        except Exception:
            raise ValueError(f"Error while calling action: {action}")
        
        raise ValueError(f"Action does not exist: {action}")

    def _get_first_name(self, last_name: str) -> str:
        return "Gavin"
    
    def _get_last_name(self) -> str:
        return "McLaughlan"