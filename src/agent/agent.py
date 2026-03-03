from agent.llm_client import LLMClient
from agent.schema import LLMMessage
from agent.config import agent_settings
from tools.registry import registry
import json


class Agent:
    def __init__(
            self,
    ):
        self.client = LLMClient(system_prompt=agent_settings.SYSTEM_PROMPT)

    async def run(
        self, 
        messages: list[LLMMessage],
    ) -> list[LLMMessage]:
        
        tool_calls = []
        init_length = len(messages)

        for i in range(agent_settings.MAX_ITERATIONS):

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
                tool_response = await registry.call_tool(tc.name, tc.arguments)

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


    def _format_tools(self):
        return registry.formatted_tools()