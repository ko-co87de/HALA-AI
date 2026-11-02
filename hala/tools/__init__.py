"""Tools package."""
from hala.tools.filesystem import grep_files, list_files, read_file, write_file
from hala.tools.python_exec import run_python
from hala.tools.terminal import run_terminal
from hala.types import ToolCall, ToolResult

TOOL_MAP = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "grep_files": grep_files,
    "run_python": run_python,
    "run_terminal": run_terminal,
}


def get_tool(name: str):
    if name not in TOOL_MAP:
        raise ValueError(f"Unknown tool: {name}. Available: {list(TOOL_MAP)}")
    return TOOL_MAP[name]


def execute_tool(call: ToolCall) -> ToolResult:
    tool_fn = get_tool(call.tool)
    result = tool_fn(**call.arguments)
    result.tool_call_id = call.id
    result.tool = call.tool
    return result


def list_tools() -> list[str]:
    return sorted(TOOL_MAP.keys())


__all__ = [
    "execute_tool", "get_tool", "list_tools", "TOOL_MAP",
    "read_file", "write_file", "list_files", "grep_files",
    "run_python", "run_terminal",
]