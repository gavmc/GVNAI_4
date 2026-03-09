from agent.schema import LLMMessage, ToolCall
from config import agent_settings
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


    async def _ollama_chat(
            self,
            model: str,
            messages: list[LLMMessage],
            tools: list[dict] = [],  # need to change at some point
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
            tool_calls = [ToolCall(id=str(uuid.uuid4()), name=tc["function"]["name"], arguments=tc["function"]['arguments']) for tc in message["tool_calls"]] if message.get("tool_calls", False) else None,
            thinking = message.thinking if message.thinking else None
        )

        