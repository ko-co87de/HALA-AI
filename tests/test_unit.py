"""Unit tests for HALA AI."""
import pytest

from hala.types import (
    Message, MessageRole, MemoryRecord, FactConfidence,
    Task, TaskStatus, ToolCall, ToolResult,
)
from hala.memory import MemoryStore, ConversationMemory, LongTermMemory
from hala.tools import list_tools, execute_tool, get_tool
from hala.tools.filesystem import read_file, write_file, list_files
from hala.tools.python_exec import run_python
from hala.tools.terminal import run_terminal
from hala.evaluation.engine import EvaluationEngine


class TestTypes:
    def test_message_creation(self):
        m = Message(role=MessageRole.USER, content="hello")
        assert m.role == MessageRole.USER
        assert m.content == "hello"

    def test_task_status(self):
        t = Task(description="test")
        assert t.status == TaskStatus.PENDING
        assert t.id is not None

    def test_tool_call(self):
        c = ToolCall(tool="read_file", arguments={"path": "x"})
        assert c.tool == "read_file"
        assert c.id is not None


class TestMemory:
    def test_add_and_search(self):
        store = MemoryStore()
        store.add_fact("The sky is blue", source="observation",
                       confidence=FactConfidence.VERIFIED)
        results = store.search("sky blue")
        assert len(results) == 1
        assert results[0].confidence == FactConfidence.VERIFIED

    def test_confidence_separation(self):
        store = MemoryStore()
        store.add_fact("verified fact", confidence=FactConfidence.VERIFIED)
        store.add_inference("inferred claim", confidence=FactConfidence.INFERRED)
        verified = store.get_verified_facts()
        assert len(verified) == 1
        assert "verified fact" in verified[0].content

    def test_conversation_memory_bounded(self):
        cm = ConversationMemory(max_messages=5)
        for i in range(10):
            cm.add(Message(role=MessageRole.USER, content=f"msg {i}"))
        assert len(cm.messages) <= 5

    def test_long_term_memory(self):
        ltm = LongTermMemory()
        ltm.remember("fact one", type_="fact")
        results = ltm.recall("fact")
        assert len(results) >= 1


class TestTools:
    def test_list_tools(self):
        tools = list_tools()
        assert "read_file" in tools
        assert "write_file" in tools
        assert "run_python" in tools
        assert "run_terminal" in tools

    def test_get_tool_unknown(self):
        with pytest.raises(ValueError):
            get_tool("nonexistent_tool")

    def test_read_file(self, tmp_path):
        p = tmp_path / "test.txt"
        p.write_text("hello world")
        result = read_file(str(p))
        assert result.success
        assert "hello world" in result.output

    def test_write_file(self, tmp_path):
        p = tmp_path / "subdir" / "out.txt"
        result = write_file(str(p), "content")
        assert result.success
        assert p.read_text() == "content"

    def test_run_python(self):
        result = run_python("print(2 + 2)")
        assert result.success
        assert "4" in result.output

    def test_run_python_error(self):
        result = run_python("raise ValueError('test error')")
        assert not result.success
        assert "ValueError" in result.error

    def test_run_terminal_blocked(self):
        result = run_terminal("sudo rm -rf /")
        assert not result.success
        assert "blocked" in (result.error or "").lower()

    def test_run_terminal_allowed(self):
        result = run_terminal("echo hello")
        assert result.success
        assert "hello" in result.output

    def test_execute_tool(self):
        call = ToolCall(tool="run_python", arguments={"code": "print('ok')"})
        result = execute_tool(call)
        assert result.success
        assert "ok" in result.output


class TestEvaluation:
    def test_add_and_generate(self):
        engine = EvaluationEngine()
        engine.add_test("test1", "unit", True, "ok")
        engine.add_test("test2", "unit", False, "fail", "error")
        report = engine.generate_report()
        assert report.summary["total"] == 2
        assert report.summary["passed"] == 1
        assert report.summary["failed"] == 1

    def test_run_test(self):
        engine = EvaluationEngine()
        engine.run_test("passing", "unit", lambda: True)
        engine.run_test("failing", "unit", lambda: (_ for _ in ()).throw(ValueError("x")))
        assert engine.tests[0].passed
        assert not engine.tests[1].passed

    def test_report_serialization(self):
        engine = EvaluationEngine()
        engine.add_test("t", "cat", True)
        report = engine.generate_report()
        data = report.model_dump_json()
        assert "summary" in data