from agent.schema import LLMMessage, ToolCall
from config import agent_settings
from typing import AsyncIterator
import ollama
import uuid



class LLMClient:
    def __init__(self, system_prompt: str):
        self.client = ollama.AsyncClient(agent_settings.HOST) if agent_settings.HOST else ollama.AsyncClient()
        self.system_prompt = system_prompt

    async def chat(
            self, 
            model: str,
            messages: list[LLMMessage],
            tools: list[dict] = [],  # need to change at some point
    ) -> LLMMessage:
        
        if agent_settings.PROVIDER == "ollama":
            return await self._ollama_chat(model, messages, tools)
        
        raise ValueError(f"Unsupported provider: {agent_settings.PROVIDER}")
    
    async def chat_stream(
            self,
            model: str,
            messages: list[LLMMessage],
            tools: list[dict] = []
    ) -> AsyncIterator[dict]:
        
        if agent_settings.PROVIDER == "ollama":
            async for chunk in self._ollama_chat_stream(model, messages, tools):
                yield chunk
        else:
            raise ValueError(f"Unsupported provider: {agent_settings.PROVIDER}")


    async def _build_ollama_chat(
            self,
            messages,
    ) -> LLMMessage:
        ollama_messages = []

        if agent_settings.SYSTEM_PROMPT:
            ollama_messages.append({'role': 'system', 'content': self.system_prompt})

        for msg in messages:

            if msg.role == "system":
                continue

            current_msg = {'role': msg.role}

            if msg.content:
                current_msg['content'] = msg.content

            if msg.tool_calls:
                current_msg["tool_calls"] = [
                    {
                        "function": {
                            "name": tc.name,
                            "arguments": tc.arguments,
                        },
                    } for tc in msg.tool_calls
                ]
            

            if msg.tool_name:
                current_msg["name"] = msg.tool_name

            ollama_messages.append(current_msg)
        
        return ollama_messages


    async def _ollama_chat(
            self,
            model: str,
            messages: list[LLMMessage],
            tools: list[dict] = [],
    ) -> LLMMessage:
        
        ollama_messages = await self._build_ollama_chat(messages)

        response = await self.client.chat(
            model=model, 
            messages=ollama_messages,
            tools=tools,
            think=True,
        )

        message = response["message"]

        return LLMMessage(
            role = 'assistant',
            content = message.content,
            tool_calls = [
                ToolCall(
                    id=str(uuid.uuid4()),
                    name=tc["function"]["name"], 
                    arguments=tc["function"]['arguments']
                ) for tc in message["tool_calls"]
            ] if message.get("tool_calls", False) else None,
            thinking = message.thinking if message.thinking else None
        )
    
    async def _ollama_chat_stream(
            self,
            model: str,
            messages: list[LLMMessage],
            tools: list[dict] = [],
    ) -> AsyncIterator[dict]:
        
        ollama_messages = await self._build_ollama_chat(messages)

        stream = await self.client.chat(
            model=model, 
            messages=ollama_messages,
            tools=tools,
            think=True,
            stream=True
        )

        full_content = ""
        full_thinking = ""
        tool_calls = []

        async for chunk in stream:
            message = chunk.get("message", {})

            thinking_token = message.thinking or ""
            if thinking_token:
                full_thinking += thinking_token
                yield {"type": "thinking", "text": thinking_token}
 
            content_token = message.content or ""
            if content_token:
                full_content += content_token
                yield {"type": "token", "text": content_token}
            if message.get("tool_calls"):
                tool_calls = [
                    ToolCall(
                        id=str(uuid.uuid4()),
                        name=tc["function"]["name"], 
                        arguments=tc["function"]['arguments'],
                    ) for tc in message["tool_calls"]
                ]

        yield {
            "type": "done",
            "message": LLMMessage(
                role='assistant',
                content=full_content,
                thinking=full_thinking or None,
                tool_calls=tool_calls or None,
            )
        }

        