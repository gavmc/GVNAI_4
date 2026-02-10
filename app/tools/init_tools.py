from app.tools.builtin.test_tool import TestTool
from app.tools.registry import registry


def register_all_tools():
    registry.register(TestTool())
