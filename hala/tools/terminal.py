"""Terminal command execution tool (sandboxed, no shell injection)."""
from __future__ import annotations

import subprocess
from typing import Any

from hala.types import ToolResult

# Allowlist of safe commands only
ALLOWED_COMMANDS = {
    "ls", "cat", "head", "tail", "wc", "sort", "uniq", "grep", "find",
    "pwd", "echo", "date", "python3", "python", "pip3", "pip",
    "git", "mkdir", "rm", "cp", "mv", "touch", "chmod",
}

BLOCKED_COMMANDS = {
    "sudo", "su", "rm -rf /", "dd", "mkfs", "shutdown", "reboot",
    "curl", "wget", "nc", "netcat", "bash -c", "sh -c",
}


def run_terminal(command: str, timeout: int = 30, workdir: str = ".") -> ToolResult:
    """Execute a safe terminal command."""
    parts = command.strip().split()
    if not parts:
        return ToolResult(tool_call_id="", tool="run_terminal",
                          success=False, output="", error="Empty command")

    base = parts[0]
    if base in BLOCKED_COMMANDS:
        return ToolResult(tool_call_id="", tool="run_terminal",
                          success=False, output="",
                          error=f"Command blocked for safety: {base}")
    if base not in ALLOWED_COMMANDS:
        return ToolResult(tool_call_id="", tool="run_terminal",
                          success=False, output="",
                          error=f"Command not in allowlist: {base}")

    try:
        result = subprocess.run(
            parts, capture_output=True, text=True,
            timeout=timeout, cwd=workdir,
        )
        output = result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        return ToolResult(
            tool_call_id="", tool="run_terminal",
            success=result.returncode == 0, output=output,
            error=None if result.returncode == 0 else f"Exit code: {result.returncode}",
        )
    except subprocess.TimeoutExpired:
        return ToolResult(tool_call_id="", tool="run_terminal",
                          success=False, output="",
                          error=f"Command timed out after {timeout}s")
    except Exception as exc:
        return ToolResult(tool_call_id="", tool="run_terminal",
                          success=False, output="", error=str(exc))