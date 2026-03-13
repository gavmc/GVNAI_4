from agent.llm_client import LLMClient, LLMMessage
from config import summarizer_settings


class Summarizer:
    def __init__(
            self,
    ):
        self.client = LLMClient(system_prompt=summarizer_settings.SYSTEM_PROMPT)

    async def run(
        self, 
        message: LLMMessage,
    ) -> LLMMessage:

        response = await self.client.chat(
            model=summarizer_settings.MODEL_NAME,
            messages=[message],
            think=False,
        )

        return response
