from agent.llm_client import LLMClient, LLMMessage
from agent.agent import Agent
from tools.registry import registry
from tools.builtin.test_tool import TestTool
import asyncio


client = LLMClient(provider="ollama")

orc_agent = Agent(
    model="qwen3:8b",
    host="http://127.0.0.1:11434",
    provider="ollama",
    system_prompt="You are GVNAI, a helpful assistant",
)

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
    print(result)


print("\n\n")
asyncio.run(run())
