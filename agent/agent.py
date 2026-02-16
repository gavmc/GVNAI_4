from agent.llm_client import LLMClient, LLMMessage
from tools.registry import registry
from typing import Literal, Optional, List


class Agent:
    def __init__(
            self,
            model: str,
            provider: Literal["ollama"],
            system_prompt: str,
            host: Optional[str] = None,
    ):
        self.client = LLMClient(provider, host)
        self.model = model
        self.system_prompt = system_prompt

    async def run(
        self, 
        messages: List[LLMMessage],
        max_iterations: int = 15,   # needs to be set in settings later
    ) -> LLMMessage:
        
        tool_calls = []

        for i in range(max_iterations):

            response = await self.client.chat(
                model=self.model,
                messages=messages,
                tools=self._format_tools(),
                system_prompt=self.system_prompt
            )


            if not response.tool_calls:
                return LLMMessage(
                    role='assistant',
                    content=response.content,
                    tool_calls=tool_calls,
                )
            
            for tc in response.tool_calls:
                tool_calls.append(tc)
                tool_response = registry.call_tool(tc.name, tc.arguments)

                messages.append(LLMMessage(
                    role='tool',
                    content=str(tool_response),
                    tool_name=tc.name,
                ))

                print(messages[-1])
                print()

        return LLMMessage(
            role='assistant',
            content='Max iterations',
            tool_calls=tool_calls,
        )


    def _format_tools(self):
        return registry.formatted_tools()