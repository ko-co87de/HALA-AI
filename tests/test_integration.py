"""Integration tests for HALA AI."""
import pytest

from hala.core.coordinator import Coordinator
from hala.tools import execute_tool
from hala.types import ToolCall


class TestCoordinator:
    def test_run_simple_task(self):
        coord = Coordinator()
        result = coord.run("What is 2+2? Use the run_python tool to calculate.")
        assert result.task_id is not None
        assert result.duration_ms >= 0

    def test_run_with_tool(self):
        coord = Coordinator()
        result = coord.run("Use run_python to print hello")
        assert result.task_id is not None

    def test_multiple_runs(self):
        coord = Coordinator()
        r1 = coord.run("Task one")
        r2 = coord.run("Task two")
        assert r1.task_id != r2.task_id


class TestToolIntegration:
    def test_python_then_terminal(self):
        r1 = execute_tool(ToolCall(
            tool="run_python", arguments={"code": "x = 10 + 5\nprint(x)"}
        ))
        assert r1.success
        assert "15" in r1.output

        r2 = execute_tool(ToolCall(
            tool="run_terminal", arguments={"command": "echo done"}
        ))
        assert r2.success
        assert "done" in r2.output