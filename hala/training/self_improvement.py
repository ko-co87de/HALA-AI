"""Self-Improvement Engine: research → idea → candidates → implement → red team → evaluate → compare → accept/reject."""
from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

from hala.evaluation.engine import EvaluationEngine, EvaluationReport
from hala.redteam import RedTeam


class SelfImprovementEngine:
    """Evolutionary self-improvement loop."""

    def __init__(self, workdir: str = "experiments"):
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.history: list[dict[str, Any]] = []
        self.best_report: Optional[EvaluationReport] = None
        self.best_score: float = 0.0

    def run_cycle(self, task_description: str, baseline_fn: Any,
                  candidate_fn: Any, evaluator_fn: Any,
                  max_candidates: int = 3) -> dict[str, Any]:
        """Run one self-improvement cycle."""
        cycle = {
            "task": task_description,
            "timestamp": time.time(),
            "candidates": [],
            "accepted": None,
            "reason": "",
        }

        # 1. Baseline
        baseline_report = self._run_eval(baseline_fn, evaluator_fn, "baseline")
        self.best_report = baseline_report
        self.best_score = baseline_report.summary.get("rate", 0)

        # 2. Generate and test candidates
        for i in range(max_candidates):
            candidate_name = f"candidate_{i+1}"
            candidate_dir = self.workdir / candidate_name
            candidate_dir.mkdir(parents=True, exist_ok=True)

            try:
                candidate_fn(candidate_dir, i)
                report = self._run_eval(candidate_fn, evaluator_fn, candidate_name,
                                        workdir=str(candidate_dir))
                score = report.summary.get("rate", 0)

                # Red team the candidate
                redteam = RedTeam()
                redteam.run_all(lambda t: candidate_fn(candidate_dir, t) if False else None)
                rt_report = redteam.generate_report(self.best_report)
                rt_score = rt_report.summary.get("rate", 0)

                improved = score > self.best_score and rt_score >= self.best_score * 0.9

                cycle["candidates"].append({
                    "name": candidate_name,
                    "score": score,
                    "redteam_score": rt_score,
                    "improved": improved,
                    "report": report.model_dump(),
                })

                if improved:
                    self.best_report = report
                    self.best_score = score
                    cycle["accepted"] = candidate_name
                    cycle["reason"] = (
                        f"Score improved from {baseline_report.summary.get('rate', 0):.3f} "
                        f"to {score:.3f}"
                    )
                    break
            except Exception as exc:
                cycle["candidates"].append({
                    "name": candidate_name,
                    "error": str(exc),
                    "improved": False,
                })

        if cycle["accepted"] is None:
            cycle["reason"] = "No candidate improved over baseline"

        self.history.append(cycle)
        self._save_history()
        return cycle

    def _run_eval(self, fn: Any, evaluator_fn: Any, name: str,
                  workdir: str = ".") -> EvaluationReport:
        engine = EvaluationEngine(version=name, model=name)
        evaluator_fn(engine, fn, workdir)
        return engine.generate_report(self.best_report)

    def _save_history(self) -> None:
        path = self.workdir / "history.json"
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2, default=str)

    def rollback(self) -> bool:
        """Revert to the previous best version."""
        if len(self.history) < 2:
            return False
        self.history.pop()
        if self.history:
            prev = self.history[-1]
            self.best_score = prev.get("score", 0)
        return True