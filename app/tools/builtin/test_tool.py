from typing import Dict, Any

from app.tools.base import BaseTool, ToolAction, ToolCategory, ToolParameter, ToolResult



class TestTool(BaseTool):

    @property
    def name(self) -> str:
        return "test tool"
    
    @property
    def display_name(self) -> str:
        return "test tool"
    
    @property
    def description(self) -> str:
        return "A tool to test tool use"
    
    @property
    def category(self):
        return ToolCategory.CUSTOM
    
    @property
    def is_connector(self) -> bool:
        return False

    def get_actions(self):
        return [
            ToolAction(
                name="test",
                description="A tool to test the tool use",
                parameters=[
                    ToolParameter(name="name", type="string", description="A random persons name"),
                ],
            )
        ]
    
    async def execute(self, action: str, params: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        
        handlers = {
            "test": self._repeat_name,
        }

        handler = handlers.get(action)

        if not handler:
            return ToolResult(success=False, error=f"Unknown action: {action}")
        
        return await handler(params)

    async def _repeat_name(self, params: Dict[str, Any]):
        return ToolResult(success=True, data={"msg": f"hello {params["name"]}"})