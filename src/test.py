from agent.llm_client import LLMClient, LLMMessage
from agent.agent import Agent
from tools.registry import registry
from tools.builtin.test_tool import TestTool
import asyncio


client = LLMClient()

orc_agent = Agent()

registry.register(TestTool())

async def run():

    user_message = LLMMessage(
        role='user',
        content="What is my full name?",
    )

    result = await orc_agent.run(
        messages=[user_message],
    )


    print("\n\n")
    print("Thinking: ", result.thinking)
    print("\n")
    print("Content: ", result.content)
    print("\n")
    print("Tool calls: ", result.tool_calls)
    print("\n")


print("\n\n")
asyncio.run(run())
