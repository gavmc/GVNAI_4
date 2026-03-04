from tools.schema import ToolAction, ToolParameter
from tools.base import Base
from core.sandbox import get_client
from typing import Any


class Sandbox(Base):
    def __init__(self):
        pass
    
    @property
    def name(self) -> str:
        return "sandbox"
    
    @property
    def description(self) -> str:
        return "Execute Python code or shell commands in an isolated sandbox environment"
    
    @property
    def actions(self) -> list[ToolAction]:
        return [
            ToolAction(
                name="run_shell",
                description="Run shell code and return the output",
                parameters=[ToolParameter(
                    name="command",
                    type="string",
                    description="The shell command to run",
                    required=True
                )],
                type="object"
            ),
            ToolAction(
                name="run_python",
                description="Run python code and return the output",
                parameters=[ToolParameter(
                    name="code",
                    type="string",
                    description="The python code to run",
                    required=True
                )],
                type="object"
            ),
        ]
    
    @property
    def active(self) -> bool:
        return True
    
    @property
    def connection(self) -> bool:
        return True

    async def call_action(self, action: str, arguments: dict[str, Any], context: dict[str, Any]) -> Any:

        try:
            if action == "run_shell":
                return self._run_shell(**arguments)

        except Exception:
            raise ValueError(f"Error while calling action: {action}")
        
        raise ValueError(f"Action does not exist: {action}")

    def _run_shell(self, command: str) -> str:
        client = get_client()
    