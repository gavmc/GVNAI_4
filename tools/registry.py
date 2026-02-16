from tools.base import Base
from typing import List, Dict, Any


class Registry:
    def __init__(self):
        self.connections: Dict[str, Base] = {}

    def register(self, connection: Base):
        self.connections[connection.name] = connection

    def formatted_tools(self) -> List[Dict[str, Any]]:
        tools = []

        for conn in self.connections.values():
            if conn.active:
                tools.extend(conn.formatted)

        return tools
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        connection, action = name.split("__")

        if not connection or not action:
            raise ValueError(f"Invalid tool name: {name}")
        
        if self.connections.get(connection, None):
            return self.connections[connection].call_action(action, arguments)
        
        raise ValueError(f"Connection was not registered: {connection}")
    
    def summarize_tools(self) -> List[Dict[str, Any]]:
        tools = []

        for conn in self.connections.values():
            if conn.active:
                tools.extend(conn.summary_formatted)

        return tools


    
registry = Registry()



    
