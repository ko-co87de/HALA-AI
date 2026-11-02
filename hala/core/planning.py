"""Planning engine: decompose tasks into subtasks."""
from __future__ import annotations

import json
import re
from typing import Any

from hala.models import ModelRouter
from hala.types import Message, MessageRole, Task, TaskStatus


def decompose(router: ModelRouter, task: Task, max_subtasks: int = 5) -> list[Task]:
    """Decompose a task into ordered subtasks."""
    system = Message(
        role=MessageRole.SYSTEM,
        content=(
            "You are a planning agent. Break the task into ordered subtasks. "
            "Respond with a JSON array of objects with 'description' fields only. "
            "Example: [{\"description\": \"step 1\"}, {\"description\": \"step 2\"}]"
        ),
    )
    user = Message(role=MessageRole.USER, content=task.description)
    raw = router.complete([system, user], max_tokens=512, temperature=0.0)

    try:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            items = json.loads(match.group())
            subtasks = []
            for item in items[:max_subtasks]:
                subtask = Task(
                    description=item.get("description", str(item)),
                    parent_id=task.id,
                )
                subtasks.append(subtask)
            return subtasks
    except Exception:
        pass

    # Fallback: treat whole task as single subtask
    return [task]


def make_plan(router: ModelRouter, task: Task) -> str:
    """Produce a human-readable plan for a task."""
    system = Message(
        role=MessageRole.SYSTEM,
        content="You are a planning agent. Produce a numbered step-by-step plan.",
    )
    user = Message(role=MessageRole.USER, content=task.description)
    return router.complete([system, user], max_tokens=512, temperature=0.0)