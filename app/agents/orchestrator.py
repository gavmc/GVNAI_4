from app.agents.llm_client import LLMClient, LLMMessage, LLMToolCall
from app.tools.registry import registry
from app.core.config import settings
from app.models.models import Conversation, Message
from sqlalchemy.orm import Session
from sqlalchemy import UUID
from typing import List, Dict, Any, Optional


SYSTEM_PROMPT = """You are GVNAI, an AI business assistant that helps small businesses manage their operations.

You have access to tools that let you take real actions: send emails, create invoices, manage contacts, track tasks, and more. You are not just a chatbot — you execute.

## Core Principles
- **Act, don't just advise.** If the user asks you to send an invoice, send it. Don't just explain how.
- **Confirm destructive actions.** Before sending emails, creating invoices, or modifying data, briefly confirm with the user.
- **Use the right tool.** If the business has QuickBooks connected, use that for invoicing. If not, use the built-in invoicing tool.
- **Create workflows for repeated tasks.** If the user describes a multi-step process they do regularly, offer to create a reusable workflow.
- **Be concise and direct.** These are busy business owners. Get to the point.

## Available Tool Categories
{tool_summary}

Always prioritize taking action over explaining. If you can do it, do it."""


class AgentOrchestrator:
    def __init__(self, db: Session, organization_id: UUID, user_id: UUID):
        self.llm = LLMClient("ollama", "qwen3:8b")  # can update this later
        self.max_iterations = settings.AGENT_MAX_ITERATIONS

        self.db = db
        self.organization_id = organization_id
        self.user_id = user_id

    async def run(self, user_message: str, conversation_id: Optional[UUID]) -> Dict[str, Any]:

        available_tools = registry.get_llm_functions(self.db, self.organization_id)

        tool_summary = self._build_tool_summary()
        system = SYSTEM_PROMPT.format(tool_summary=tool_summary)

        history = self._load_history(conversation_id)

        all_tool_calls = []

        for iteration in range(self.max_iterations):

            response = await self.llm.chat(messages=history, tools=available_tools, system_prompt=system)

            if not response.tool_calls:
                return {
                    "response": response,
                    "tool_calls": all_tool_calls,
                }
            
            history.append(
                LLMMessage(
                    role='assistant',
                    content=response.content,
                    tool_calls=[{
                        "id": tc.id,
                        "function_name": tc.function_name,
                        "arguments": tc.arguments,
                    } for tc in response.tool_calls]
                )
            )


            for tool_call in response.tool_calls:

                try:
                    tool_name, action_name = registry.parse_function_call(tool_call.function_name)
                except ValueError:
                    result_text = f"Invalid tool call format: {tool_call.function_name}"
                    history.append(LLMMessage(
                        role="tool", content=result_text, tool_call_id=tool_call.id
                    ))
                    continue

                context = {}

                result = await registry.execute(tool_name, action_name, tool_call.arguments, context)

                all_tool_calls.append({
                    "tool": tool_call.function_name,
                    "params": tool_call.arguments,
                    "result": result.data if result.success else result.error,
                    "success": result.success,
                })

                history.append(LLMMessage(
                    role='tool',
                    content=result.to_agent_message(),
                    tool_call_id=tool_call.id,
                ))

        final_msg = "I've completed what I could. Let me know if you need anything else."
        return {
            "response": final_msg,
            "tool_calls": all_tool_calls,
        }




    def _build_tool_summary(self) -> str:
        tools = registry.get_available_tools(self.db, self.organization_id)
        categories = {}
        for tool in tools:
            cat = tool.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(f"- **{tool.display_name}**: {tool.description}")

        lines = []
        for cat, tool_lines in categories.items():
            lines.append(f"\n### {cat.title()}")
            lines.extend(tool_lines)

        return "\n".join(lines)
    

    def _load_history(self, conversation_id: UUID) -> List[LLMMessage]:
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .all()
        )
        return [
            LLMMessage(role=m.role, content=m.content, tool_calls=m.tool_calls)
            for m in messages
        ]

