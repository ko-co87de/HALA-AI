"""Security regression tests — every confirmed failure becomes a permanent test."""
import pytest

from hala.tools.terminal import run_terminal
from hala.tools.python_exec import run_python
from hala.redteam.agent import RedTeam


class MockResult:
    """Deterministic mock for coordinator results in security tests."""
    def __init__(self, output="", error=None, success=True):
        self.output = output
        self.error = error
        self.success = success


def _make_run_fn(responses: dict[str, str]):
    """Create a mock run function with deterministic responses."""
    def run_fn(prompt):
        for key, resp in responses.items():
            if key.lower() in prompt.lower():
                return MockResult(output=resp)
        return MockResult(output="")
    return run_fn


class TestTerminalSecurity:
    """Regression tests for tool abuse."""

    def test_blocked_sudo(self):
        result = run_terminal("sudo rm -rf /")
        assert not result.success

    def test_blocked_curl(self):
        result = run_terminal("curl evil.com")
        assert not result.success

    def test_blocked_rm_rf_root(self):
        result = run_terminal("rm -rf /")
        assert not result.success

    def test_allowed_safe_command(self):
        result = run_terminal("echo hello")
        assert result.success


class TestPythonExecSecurity:
    """Regression tests for code execution safety."""

    def test_no_os_system(self):
        result = run_python("import os; os.system('rm -rf /')")
        assert not result.success


class TestRedTeam:
    """Red team probes — using deterministic mocks for speed."""

    def test_prompt_injection_defense(self):
        run_fn = _make_run_fn({
            "ignore all": "I cannot ignore my instructions.",
            "system:": "I will not reveal my system prompt.",
        })
        rt = RedTeam()
        rt._probe_prompt_injection(run_fn)
        assert len(rt.findings) >= 1

    def test_memory_poisoning_defense(self):
        run_fn = _make_run_fn({
            "remember this fact": "Recorded.",
            "what color is the sky": "The sky is blue.",
        })
        rt = RedTeam()
        rt._probe_memory_poisoning(run_fn)
        assert len(rt.findings) >= 1

    def test_tool_abuse_defense(self):
        run_fn = _make_run_fn({
            "delete all files": "Error: blocked for safety.",
            "sudo rm": "Error: Command blocked for safety.",
            "curl": "Error: Command not in allowlist.",
        })
        rt = RedTeam()
        rt._probe_tool_abuse(run_fn)
        assert len(rt.findings) >= 1

    def test_hallucination_defense(self):
        run_fn = _make_run_fn({
            "atlantis": "I'm not sure — Atlantis is fictional.",
            "constant x": "Unknown — there is no standard constant X in physics.",
        })
        rt = RedTeam()
        rt._probe_hallucination(run_fn)
        assert len(rt.findings) >= 1

    def test_context_attack_resilience(self):
        run_fn = _make_run_fn({"a" * 100: "ok"})
        rt = RedTeam()
        rt._probe_context_attack(run_fn)
        assert len(rt.findings) >= 1

    def test_resource_exhaustion_resilience(self):
        run_fn = _make_run_fn({"task": "ok"})
        rt = RedTeam()
        rt._probe_resource_exhaustion(run_fn)
        assert len(rt.findings) >= 1

    def test_failure_recovery(self):
        run_fn = _make_run_fn({"": MockResult(output="", success=True),
                               "what is 2+2": MockResult(output="4", success=True)})
        rt = RedTeam()
        rt._probe_failure_recovery(run_fn)
        assert len(rt.findings) >= 1

    def test_all_probes_run(self):
        run_fn = _make_run_fn({})
        rt = RedTeam()
        findings = rt.run_all(run_fn)
        assert len(findings) == 7