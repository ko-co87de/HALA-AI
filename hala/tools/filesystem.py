"""Filesystem tools."""
from __future__ import annotations

import os
from typing import Any

from hala.types import ToolCall, ToolResult


def read_file(path: str) -> ToolResult:
    try:
        if not os.path.exists(path):
            return ToolResult(tool_call_id="", tool="read_file",
                              success=False, output="",
                              error=f"File not found: {path}")
        with open(path, "r", errors="replace") as f:
            content = f.read()
        return ToolResult(tool_call_id="", tool="read_file",
                          success=True, output=content)
    except Exception as exc:
        return ToolResult(tool_call_id="", tool="read_file",
                          success=False, output="", error=str(exc))


def write_file(path: str, content: str) -> ToolResult:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return ToolResult(tool_call_id="", tool="write_file",
                          success=True, output=f"Wrote {len(content)} bytes to {path}")
    except Exception as exc:
        return ToolResult(tool_call_id="", tool="write_file",
                          success=False, output="", error=str(exc))


def list_files(path: str = ".") -> ToolResult:
    try:
        entries = sorted(os.listdir(path))
        return ToolResult(tool_call_id="", tool="list_files",
                          success=True, output="\n".join(entries))
    except Exception as exc:
        return ToolResult(tool_call_id="", tool="list_files",
                          success=False, output="", error=str(exc))


def grep_files(pattern: str, path: str = ".") -> ToolResult:
    try:
        import re
        matches = []
        regex = re.compile(pattern)
        for root, _, files in os.walk(path):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", errors="replace") as f:
                        for i, line in enumerate(f, 1):
                            if regex.search(line):
                                matches.append(f"{fpath}:{i}: {line.rstrip()}")
                except Exception:
                    continue
        return ToolResult(tool_call_id="", tool="grep_files",
                          success=True, output="\n".join(matches[:100]))
    except Exception as exc:
        return ToolResult(tool_call_id="", tool="grep_files",
                          success=False, output="", error=str(exc))