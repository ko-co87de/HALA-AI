"""Sandboxed Python code execution tool."""
from __future__ import annotations

import contextlib
import io
import os
import sys
import traceback
from typing import Any

from hala.types import ToolResult


def run_python(code: str, timeout: int = 30) -> ToolResult:
    """Execute Python code in a restricted namespace with output capture."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    namespace: dict[str, Any] = {"__name__": "__hala_python__", "__builtins__": {
        k: v for k, v in __builtins__.items()
        if k in (
            "print", "len", "range", "str", "int", "float", "bool", "list",
            "dict", "set", "tuple", "type", "isinstance", "sorted", "reversed",
            "enumerate", "zip", "map", "filter", "sum", "min", "max", "abs",
            "round", "open", "repr", "format", "Exception", "ValueError",
            "TypeError", "KeyError", "IndexError", "RuntimeError", "True",
            "False", "None", "range",
        )
    }}

    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exec(compile(code, "<hala-python>", "exec"), namespace)
        return ToolResult(
            tool_call_id="", tool="run_python", success=True,
            output=stdout.getvalue() or "(no output)",
        )
    except Exception:
        return ToolResult(
            tool_call_id="", tool="run_python", success=False, output="",
            error=traceback.format_exc(),
        )