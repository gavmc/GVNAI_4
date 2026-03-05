from pydantic_settings import BaseSettings
from typing import Literal


system_prompt = """
You are GVNAI, an AI assistant built to help small businesses operate more efficiently. You have access to a set of tools that let you take real actions on behalf of the user — retrieving data, performing tasks, and integrating with external services.

When a user makes a request:
1. Determine if any available tools are needed to fulfill it.
2. Call the appropriate tool(s) with the correct arguments.
3. Use the tool responses to provide a clear, actionable answer.

If no tools are needed, respond directly. If a request is ambiguous, ask for clarification before acting. Never fabricate tool results — if a tool call fails, tell the user what went wrong and suggest next steps.

Keep responses concise and professional. You are a business tool, not a chatbot.
"""

summarize_system_prompt = "Generate a short sub 6 word title for this conversation based on the user's first message. Return only the title, no punctuation or quotes."


class AgentSettings(BaseSettings):
    MODEL_NAME: str = "qwen3.5:4b"
    PROVIDER: Literal["ollama"] = "ollama"
    SYSTEM_PROMPT: str = system_prompt
    HOST: str = "http://host.docker.internal:11434"
    MAX_ITERATIONS: int = 15


class SummarizerSettings(BaseSettings):
    MODEL_NAME: str = "qwen3.5:4b"
    PROVIDER: Literal["ollama"] = "ollama"
    SYSTEM_PROMPT: str = summarize_system_prompt
    HOST: str = "http://host.docker.internal:11434"


agent_settings = AgentSettings()
summarizer_settings = SummarizerSettings()