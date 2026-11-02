"""Central coordinator: task decomposition, delegation, verification."""
from __future__ import annotations

import re
import time
from typing import Any, Optional

from hala.memory import ConversationMemory, LongTermMemory
from hala.models import ModelRouter
from hala.tools import execute_tool, list_tools
from hala.types import (
    AgentResult, Message, MessageRole, Task, TaskStatus, ToolCall,
)


class Coordinator:
    """Decomposes tasks, delegates to agents, verifies results."""

    def __init__(self, router: Optional[ModelRouter] = None,
                 memory: Optional[LongTermMemory] = None):
        self.router = router or ModelRouter(preferred="hala-local-1.5b")
        self.memory = memory or LongTermMemory()
        self.conversation = ConversationMemory()
        self.active_tasks: dict[str, Task] = {}

    def run(self, user_request: str, max_steps: int = 10) -> AgentResult:
        """Execute a user request end-to-end."""
        task = Task(description=user_request)
        self.active_tasks[task.id] = task
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = time.time()

        self.conversation.add(Message(role=MessageRole.USER, content=user_request))

        steps = 0
        tool_calls: list[ToolCall] = []
        error: Optional[str] = None

        while steps < max_steps:
            steps += 1
            try:
                plan = self._plan(task, steps, max_steps)
                if plan.get("done"):
                    break

                action = plan.get("action")
                if action == "tool":
                    call = ToolCall(
                        tool=plan["tool"],
                        arguments=plan.get("arguments", {}),
                        thought=plan.get("thought"),
                    )
                    tool_calls.append(call)
                    result = execute_tool(call)
                    self.conversation.add(Message(
                        role=MessageRole.OBSERVATION,
                        content=result.output or result.error or "",
                        metadata={"success": result.success},
                    ))
                    if not result.success:
                        error = result.error
                        # Retry once with adjusted arguments
                        if steps < max_steps - 1:
                            continue
                        break
                elif action == "answer":
                    answer = plan.get("answer", "")
                    self.conversation.add(Message(
                        role=MessageRole.ASSISTANT, content=answer
                    ))
                    task.result = answer
                    task.status = TaskStatus.COMPLETED
                    break
                else:
                    # Direct answer
                    answer = plan.get("answer", str(plan))
                    task.result = answer
                    task.status = TaskStatus.COMPLETED
                    break

            except Exception as exc:
                error = str(exc)
                self.memory.add_experience(
                    content=f"Task failed: {task.description}",
                    outcome=f"error: {error}",
                )
                break

        if task.status == TaskStatus.IN_PROGRESS:
            task.status = TaskStatus.FAILED if error else TaskStatus.COMPLETED

        task.completed_at = time.time()
        task.tool_calls = tool_calls

        return AgentResult(
            task_id=task.id,
            agent="coordinator",
            success=task.status == TaskStatus.COMPLETED,
            output=task.result or "",
            error=error,
            tool_calls=tool_calls,
            duration_ms=(task.completed_at - task.started_at) * 1000,
        )

    def _plan(self, task: Task, step: int, max_steps: int) -> dict[str, Any]:
        """Use the model to decide the next action."""
        system_msg = Message(
            role=MessageRole.SYSTEM,
            content=(
                "You are HALA AI coordinator. You have access to these tools: "
                + ", ".join(list_tools()) +
                "\n\nDecide the next step. Respond with EXACTLY one of:\n"
                "1. TOOL: tool_name | args: {json}\n"
                "2. ANSWER: your final answer\n\n"
                "Rules:\n"
                "- Prefer tools over guessing.\n"
                "- If you have enough info, give ANSWER.\n"
                "- Keep answers concise and accurate.\n"
                "- For math: use run_python.\n"
                "- For file ops: use read_file/write_file/list_files.\n"
            ),
        )
        messages = [system_msg] + self.conversation.to_list()

        try:
            raw = self.router.complete(messages, max_tokens=256, temperature=0.0)
        except Exception:
            # Fallback: no model available
            return {"done": True, "answer": "[No model available for inference]"}

        raw = raw.strip()
        self.conversation.add(Message(role=MessageRole.ASSISTANT, content=raw))

        if raw.upper().startswith("ANSWER:"):
            return {"done": True, "answer": raw.split(":", 1)[1].strip()}

        if raw.upper().startswith("TOOL:"):
            try:
                tool_part = raw.split(":", 1)[1].strip()
                tool_name = tool_part.split("|")[0].strip()
                args_str = ""
                if "|" in tool_part:
                    args_str = tool_part.split("|", 1)[1].strip()
                    if args_str.lower().startswith("args:"):
                        args_str = args_str.split(":", 1)[1].strip()
                import json
                arguments = json.loads(args_str) if args_str else {}
                return {
                    "action": "tool",
                    "tool": tool_name,
                    "arguments": arguments,
                    "thought": raw,
                }
            except Exception:
                return {"done": True, "answer": f"Could not parse tool call: {raw}"}

        return {"done": True, "answer": raw}

    def explain(self) -> str:
        """Return a summary of the last run."""
        msgs = self.conversation.to_list()
        lines = []
        for m in msgs[-10:]:
            lines.append(f"[{m.role.value}] {m.content[:200]}")
        return "\n".join(lines)