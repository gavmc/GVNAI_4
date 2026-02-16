from typing import Literal, Optional, List, Dict
from agent.schema import LLMMessage, ToolCall
import ollama
import uuid



class LLMClient:
    def __init__(
            self, 
            provider: Literal["ollama"], 
            host: Optional[str] = None,
    ):
        self.provider = provider
        self.client = ollama.AsyncClient(host) if host else ollama.AsyncClient()

    async def chat(
            self, 
            model: str,
            messages: List[LLMMessage],
            tools: List[Dict] = [],  # need to change at some point
            system_prompt: Optional[str] = None,
    ) -> LLMMessage:
        
        if self.provider == "ollama":
            return await self._ollama_chat(model, messages, tools, system_prompt)
        
        raise ValueError(f"Unsupported provider: {self.provider}")


    async def _ollama_chat(
            self,
            model: str,
            messages: List[LLMMessage],
            tools: List[Dict] = [],  # need to change at some point
            system_prompt: Optional[str] = None,
    ) -> LLMMessage:
        
        ollama_messages = []

        if system_prompt:
            ollama_messages.append({'role': 'system', 'content': system_prompt})

        for msg in messages:

            if msg.role == "system":
                continue

            current_msg = {'role': msg.role, 'content': msg.content}

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
                current_msg["tool_name"] = msg.tool_name

            ollama_messages.append(current_msg)


        response = await self.client.chat(
            model=model, 
            messages=ollama_messages,
            tools=tools,
        )

        message = response["message"]

        return LLMMessage(
            role = 'assistant',
            content = message['content'],
            tool_calls = [ToolCall(id=str(uuid.uuid4()), name=tc["function"]["name"], arguments=tc["function"]['arguments']) for tc in message["tool_calls"]] if message.get("tool_calls", False) else None,
        )

        