from pydantic import BaseModel, Field
from typing import List



class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    enum: List = Field(default_factory = list)

class ToolAction(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]
    type: str = "object"

class ToolConnection(BaseModel):
    name: str
    description: str
    actions: List[ToolAction]
    active: bool
    connection: bool