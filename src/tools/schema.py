from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    enum: list = Field(default_factory = list)

class ToolAction(BaseModel):
    name: str
    description: str
    parameters: list[ToolParameter]
    type: str = "object"

class ToolConnection(BaseModel):
    name: str
    description: str
    actions: list[ToolAction]
    active: bool
    connection: bool