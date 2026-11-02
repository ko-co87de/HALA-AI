"""HALA AI CLI entry point."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from hala.core.coordinator import Coordinator
from hala.core.reasoning import reason, reason_math
from hala.models import ModelRouter
from hala.tools import list_tools


def cmd_run(args: argparse.Namespace) -> int:
    """Run a task through the coordinator."""
    router = ModelRouter(preferred=args.model)
    coord = Coordinator(router=router)
    result = coord.run(args.task, max_steps=args.max_steps)

    print(f"Success: {result.success}")
    if result.output:
        print(f"Output: {result.output}")
    if result.error:
        print(f"Error: {result.error}", file=sys.stderr)
    print(f"Tool calls: {len(result.tool_calls)}")
    print(f"Duration: {result.duration_ms:.0f}ms")

    if args.explain:
        print("\n--- Trace ---")
        print(coord.explain())

    return 0 if result.success else 1


def cmd_reason(args: argparse.Namespace) -> int:
    """Run a reasoning task."""
    router = ModelRouter(preferred=args.model)
    if args.math:
        answer = reason_math(router, args.task)
    else:
        answer = reason(router, args.task, context=args.context or "")
    print(answer)
    return 0


def cmd_tools(args: argparse.Namespace) -> int:
    """List available tools."""
    tools = list_tools()
    print("Available tools:")
    for t in tools:
        print(f"  - {t}")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    """Run the test suite."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"] + (args.args or []),
        capture_output=False,
    )
    return result.returncode


def cmd_eval(args: argparse.Namespace) -> int:
    """Run evaluation and print report."""
    from hala.evaluation.engine import EvaluationEngine
    engine = EvaluationEngine()
    report_path = Path("reports/latest_evaluation.json")
    if report_path.exists():
        with open(report_path) as f:
            report = json.load(f)
        print(json.dumps(report.get("summary", {}), indent=2))
    else:
        print("No evaluation report found. Run tests first.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="hala",
        description="HALA AI 100X — Open-weight, self-improving AI system",
    )
    parser.add_argument("--model", default="hala-local-1.5b",
                        help="Model to use (default: local)")

    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Run a task")
    run_p.add_argument("task", help="Task description")
    run_p.add_argument("--max-steps", type=int, default=10)
    run_p.add_argument("--explain", action="store_true")
    run_p.set_defaults(func=cmd_run)

    reason_p = sub.add_parser("reason", help="Run a reasoning task")
    reason_p.add_argument("task", help="Question or problem")
    reason_p.add_argument("--math", action="store_true")
    reason_p.add_argument("--context", default="")
    reason_p.set_defaults(func=cmd_reason)

    sub.add_parser("tools", help="List available tools").set_defaults(func=cmd_tools)

    test_p = sub.add_parser("test", help="Run tests")
    test_p.add_argument("args", nargs="*")
    test_p.set_defaults(func=cmd_test)

    sub.add_parser("eval", help="Show evaluation report").set_defaults(func=cmd_eval)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    sys.exit(args.func(args))


if __name__ == "__main__":
    main()