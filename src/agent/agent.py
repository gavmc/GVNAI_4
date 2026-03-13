from agent.llm_client import LLMClient
from agent.schema import LLMMessage, StreamEvent
from config import agent_settings
from tools.registry import registry
from typing import AsyncIterator
import json


class Agent:
    def __init__(
            self,
    ):
        self.client = LLMClient(system_prompt=agent_settings.SYSTEM_PROMPT)

    async def run(
        self, 
        messages: list[LLMMessage],
        session_id: str,
    ) -> list[LLMMessage]:
        
        tool_calls = []
        init_length = len(messages)

        for _ in range(agent_settings.MAX_ITERATIONS):

            response = await self.client.chat(
                model=agent_settings.MODEL_NAME,
                messages=messages,
                tools=self._format_tools(),
            )


            if not response.tool_calls:
                messages.append(
                    LLMMessage(
                        role='assistant',
                        content=response.content,
                        tool_calls=tool_calls,
                        thinking=response.thinking
                    )
                )

                return messages[init_length:]
            
            messages.append(LLMMessage(
                role='assistant',
                content='',
                tool_calls=response.tool_calls,
            ))
            
            for tc in response.tool_calls:
                tool_calls.append(tc)
                tool_response = await registry.call_tool(tc.name, tc.arguments, {"session_id": session_id})

                messages.append(LLMMessage(
                    role='tool',
                    content=json.dumps(tool_response),
                    tool_name=tc.name,
                ))

        messages.append(
            LLMMessage(
                role='assistant',
                content='Max iterations',
                tool_calls=tool_calls,
            )
        )
        return messages[init_length:]
    

    async def run_stream(
        self,
        messages: list[LLMMessage],
        session_id: str,
    ) -> AsyncIterator[StreamEvent]:
        
        tool_calls = []

        for _ in range(agent_settings.MAX_ITERATIONS):
            current_msg: LLMMessage | None = None

            async for chunk in self.client.chat_stream(
                model=agent_settings.MODEL_NAME,
                messages=messages,
                tools=self._format_tools(),
            ):
                if chunk["type"] == "thinking":
                    yield StreamEvent(event="thinking", data=chunk["text"])

                elif chunk["type"] == "token":
                    yield StreamEvent(event="token", data=chunk["text"])

                elif chunk["type"] == "done":
                    current_msg = chunk["message"]

            if current_msg is None:
                yield StreamEvent(event="error", data="LLM returned no response")
                return
            
            if not current_msg.tool_calls:
                final = LLMMessage(
                    role='assistant',
                    content=current_msg.content,
                    thinking=current_msg.thinking,
                    tool_calls=tool_calls or None,
                )

                messages.append(final)

                yield StreamEvent(
                    event="done",
                    data=current_msg.content,
                    tool_calls=tool_calls or None,
                )
                return
            
            messages.append(LLMMessage(
                role="assistant",
                content=current_msg.content,
                tool_calls=current_msg.tool_calls,
            ))
 
            for tc in current_msg.tool_calls:
                tool_calls.append(tc)
 
                yield StreamEvent(
                    event="tool_call",
                    data=tc.name,
                    tool_call=tc,
                )
 
                try:
                    tool_response = await registry.call_tool(
                        tc.name, tc.arguments, {"session_id": session_id}
                    )
                except Exception as e:
                    tool_response = {"error": str(e)}
 
                tool_result_str = json.dumps(tool_response)
 
                messages.append(LLMMessage(
                    role="tool",
                    content=tool_result_str,
                    tool_name=tc.name,
                ))
 
                yield StreamEvent(
                    event="tool_result",
                    data=tool_result_str,
                    tool_call=tc,
                )
 
        final = LLMMessage(
            role="assistant",
            content="Max iterations reached",
            tool_calls=tool_calls,
        )
        messages.append(final)
        yield StreamEvent(event="done", data="Max iterations reached", tool_calls=tool_calls)
 

    def _format_tools(self):
        return registry.formatted_tools()