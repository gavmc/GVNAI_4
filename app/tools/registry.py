from typing import Dict, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import UUID

from app.tools.base import BaseTool, ToolCategory, ToolResult
from app.models.models import ToolConnection


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[BaseTool]:
        return list(self._tools.values())
    
    def get_builtin_tools(self) -> List[BaseTool]:
        return [t for t in self._tools.values() if not t.is_connector]
    
    def get_connector_tools(self) -> List[BaseTool]:
        return [t for t in self._tools.values() if t.is_connector]
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        return [t for t in self._tools.values() if t.category == category]
    
    def get_available_tools(self, db: Session, organization_id: UUID) -> List[BaseTool]:   
        
        available = []

        available.extend(self.get_builtin_tools())

        connections = (
            db.query(ToolConnection).filter(
                ToolConnection.organization_id == organization_id,
                ToolConnection.is_active == True,
            ).all()
        )

        connected_tool_names = {c.tool_name for c in connections}

        for tool in self.get_connector_tools():
            if tool.name in connected_tool_names:
                available.append(tool)
        
        return  available

    def get_llm_functions(self, db: Session, organization_id: UUID) -> List[Dict[str, Any]]:   
        tools = self.get_available_tools(db, organization_id)
        functions = []
        for tool in tools:
            functions.extend(tool.get_llm_schema())

        return functions
    
    async def execute(
            self,
            tool_name: str,
            action: str,
            params: Dict[str, Any],
            context: Dict[str, Any],
    ) -> ToolResult:
        
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(success=False, error=f"Unknown tool: {tool_name}")
        
        try:
            return await tool.execute(action, params, context)
        except Exception as e:
            return ToolResult(success=False, error=f"Tool execution error: {str(e)}")
        
    def parse_function_call(self, function_name: str) -> tuple[str, str]:
        parts = function_name.split("__", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid function name format: {function_name}")
        return parts[0], parts[1]
    

registry = ToolRegistry()

