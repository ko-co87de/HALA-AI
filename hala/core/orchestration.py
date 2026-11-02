"""Orchestration: tool/agent dispatch and event loop."""
from __future__ import annotations

import time
from typing import Any, Callable, Optional

from hala.core.coordinator import Coordinator
from hala.types import AgentResult, Task


class Orchestrator:
    """Runs coordinators and agents, tracks results and timing."""

    def __init__(self):
        self.runs: list[dict[str, Any]] = []

    def run_task(self, task: str, coordinator: Optional[Coordinator] = None,
                 **kwargs: Any) -> AgentResult:
        coord = coordinator or Coordinator()
        start = time.time()
        result = coord.run(task, **kwargs)
        elapsed = (time.time() - start) * 1000

        self.runs.append({
            "task": task,
            "success": result.success,
            "output": result.output[:500],
            "error": result.error,
            "duration_ms": elapsed,
            "tool_calls": len(result.tool_calls),
            "timestamp": time.time(),
        })
        return result

    def summary(self) -> str:
        if not self.runs:
            return "No runs yet."
        total = len(self.runs)
        succeeded = sum(1 for r in self.runs if r["success"])
        return (
            f"Runs: {total} | Success: {succeeded} | "
            f"Failed: {total - succeeded} | "
            f"Success rate: {succeeded/total*100:.1f}%"
        )