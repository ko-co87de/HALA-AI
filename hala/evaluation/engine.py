"""Evaluation engine: benchmarks, metrics, and reports."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class TestResult(BaseModel):
    name: str
    category: str
    passed: bool
    duration_ms: float
    details: str = ""
    error: Optional[str] = None


class EvaluationReport(BaseModel):
    version: str
    timestamp: float
    model: str
    tests: list[TestResult] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    resource_usage: dict[str, Any] = Field(default_factory=dict)
    comparison_to_previous: Optional[dict[str, Any]] = None


class EvaluationEngine:
    """Runs tests, compares against baseline, produces reports."""

    def __init__(self, version: str = "0.1.0-alpha",
                 model: str = "hala-local-1.5b"):
        self.version = version
        self.model = model
        self.tests: list[TestResult] = []
        self.report_path = Path("reports/latest_evaluation.json")

    def add_test(self, name: str, category: str, passed: bool,
                 details: str = "", error: Optional[str] = None,
                 duration_ms: float = 0.0) -> None:
        self.tests.append(TestResult(
            name=name, category=category, passed=passed,
            details=details, error=error, duration_ms=duration_ms,
        ))

    def run_test(self, name: str, category: str, fn: Any) -> None:
        """Run a test function and record the result."""
        start = time.time()
        try:
            result = fn()
            duration = (time.time() - start) * 1000
            if isinstance(result, tuple):
                passed, details = result[0], result[1]
            elif isinstance(result, bool):
                passed, details = result, ""
            else:
                passed, details = True, str(result)
            self.add_test(name, category, passed, details, duration_ms=duration)
        except Exception as exc:
            duration = (time.time() - start) * 1000
            self.add_test(name, category, False, "", str(exc), duration)

    def generate_report(self, previous: Optional["EvaluationReport"] = None) -> EvaluationReport:
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t.passed)
        failed = [t for t in self.tests if not t.passed]

        by_category: dict[str, dict[str, int]] = {}
        for t in self.tests:
            cat = t.category
            if cat not in by_category:
                by_category[cat] = {"total": 0, "passed": 0}
            by_category[cat]["total"] += 1
            if t.passed:
                by_category[cat]["passed"] += 1

        comparison = None
        if previous:
            prev_passed = sum(1 for t in previous.tests if t.passed)
            comparison = {
                "previous_total": len(previous.tests),
                "previous_passed": prev_passed,
                "previous_rate": prev_passed / len(previous.tests) if previous.tests else 0,
                "current_rate": passed / total if total else 0,
                "delta": (passed / total if total else 0) -
                         (prev_passed / len(previous.tests) if previous.tests else 0),
            }

        report = EvaluationReport(
            version=self.version,
            timestamp=time.time(),
            model=self.model,
            tests=self.tests,
            summary={
                "total": total,
                "passed": passed,
                "failed": len(failed),
                "rate": passed / total if total else 0,
                "by_category": by_category,
            },
            errors=[t.error for t in failed if t.error],
            improvements=[t.name for t in self.tests if t.passed],
            resource_usage={
                "total_duration_ms": sum(t.duration_ms for t in self.tests),
            },
            comparison_to_previous=comparison,
        )

        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w") as f:
            f.write(report.model_dump_json(indent=2))

        return report

    def clear(self) -> None:
        self.tests.clear()