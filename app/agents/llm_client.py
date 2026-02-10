from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Literal
import ollama
import json
import uuid

@dataclass
class LLMMessage:
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class LLMToolCall:
    id: str
    function_name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    content: str
    tool_calls: List[LLMToolCall] = field(default_factory=list)
    stop_reason: Literal["end_turn", "tool_use", "max_tokens"] = "end_turn"
    usage: Dict[str, int] = field(default_factory=dict)


class LLMClient:
    def __init__(
            self,
            provider: Literal["ollama"],
            model: str,
            host: Optional[str] = None,
    ):
        self.provider = provider
        self.model = model
        self.client = ollama.AsyncClient(host=host) if host else ollama.AsyncClient()

    async def chat(
            self, 
            messages: List[LLMMessage],
            tools: Optional[List[Dict[str, Any]]] = None,
            system_prompt: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: int = 4096,
    ) -> LLMResponse:
        
        if(self.provider == "ollama"):
            return await self._ollama_chat(messages, tools, system_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    

    async def _ollama_chat(
            self, 
            messages: List[LLMMessage],
            tools: Optional[List[Dict[str, Any]]] = None,
            system_prompt: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: int = 4096,
    ) -> LLMResponse:
        
        ollama_messages = []
        if system_prompt:
            ollama_messages.append({'role': 'system', 'content': system_prompt})

        for msg in messages:
            if msg.role == "system":
                continue

            if msg.role == "tool":
                ollama_messages.append({'role': 'tool', 'content': msg.content})
            
            elif msg.role == "assistant" and msg.tool_calls:
                formatted_tool_calls = []
                for tc in msg.tool_calls:
                    formatted_tool_calls.append({
                        "id": tc.get("id", str(uuid.uuid4())),
                        "type": "function",
                        "function": {
                            "name": tc["function_name"],
                            "arguments": tc["arguments"],
                        },
                    })

                ollama_messages.append({
                    'role': 'assistant',
                    'content': msg.content or "",
                    'tool_calls': formatted_tool_calls,
                })

            else:
                ollama_messages.append({'role': msg.role, 'content': msg.content})


        ollama_tools = None
        if tools:
            ollama_tools = []
            for tool in tools:
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"],
                    },
                })

        kwargs = {
            "model": self.model,
            "messages": ollama_messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        if ollama_tools:
            kwargs["tools"] = ollama_tools

        response = await self.client.chat(**kwargs)

        message = response.get("message", {})
        content = message.get("content", "")
        raw_tool_calls = message.get("tool_calls", [])

        if not raw_tool_calls:
            raw_tool_calls = []

        tool_calls = []
        for tc in raw_tool_calls:
            fn = tc.get("function", {})
            arguments = fn.get("arguments", {})

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            tool_calls.append(LLMToolCall(
                id = tc.get("id", str(uuid.uuid4())),
                function_name=fn.get("name", ""),
                arguments=arguments,
            ))

        stop_reason = "end_turn"
        if tool_calls:
            stop_reason = "tool_use"
        elif response.get("done_reason") == "length":
            stop_reason = "max_tokens"

        usage = {}
        if "prompt_eval_count" in response:
            usage["input"] = response["prompt_eval_count"]
        if "eval_count" in response:
            usage["output"] = response["eval_count"]

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            usage=usage,
        )




        
            
        
