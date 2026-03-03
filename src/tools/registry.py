from tools.base import Base
from typing import Any


class Registry:
    def __init__(self):
        self.connections: dict[str, Base] = {}

    def register(self, connection: Base):
        self.connections[connection.name] = connection

    def formatted_tools(self) -> list[dict[str, Any]]:
        tools = []

        for conn in self.connections.values():
            if conn.active:
                tools.extend(conn.formatted())

        return tools
    
    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        connection, action = name.split("__", 1)

        if not connection or not action:
            raise ValueError(f"Invalid tool name: {name}")
        
        if self.connections.get(connection, None):
            return await self.connections[connection].call_action(action, arguments)
        
        raise ValueError(f"Connection was not registered: {connection}")
    
    def summarize_tools(self) -> list[dict[str, Any]]:
        tools = []

        for conn in self.connections.values():
            if conn.active:
                tools.extend(conn.summary_formatted())

        return tools


    
registry = Registry()



    
