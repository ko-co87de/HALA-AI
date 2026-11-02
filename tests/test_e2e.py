"""End-to-end tests for HALA AI CLI."""
import subprocess
import sys
import json
from pathlib import Path


def test_cli_tools():
    result = subprocess.run(
        [sys.executable, "-m", "hala", "tools"],
        capture_output=True, text=True, cwd="/data/data/com.termux/files/home/HALA-AI",
    )
    assert result.returncode == 0
    assert "read_file" in result.stdout
    assert "run_python" in result.stdout


def test_cli_run_simple():
    result = subprocess.run(
        [sys.executable, "-m", "hala", "run",
         "Use the run_python tool to calculate 15 * 23"],
        capture_output=True, text=True, cwd="/data/data/com.termux/files/home/HALA-AI",
        timeout=180,
    )
    assert result.returncode == 0
    assert "Success: True" in result.stdout


def test_cli_reason():
    result = subprocess.run(
        [sys.executable, "-m", "hala", "reason",
         "What is 2+2? Answer with just the number."],
        capture_output=True, text=True, cwd="/data/data/com.termux/files/home/HALA-AI",
        timeout=180,
    )
    assert result.returncode == 0
    assert "4" in result.stdout


def test_evaluation_report_exists():
    report_path = Path("/data/data/com.termux/files/home/HALA-AI/reports/latest_evaluation.json")
    assert report_path.exists()
    with open(report_path) as f:
        report = json.load(f)
    assert "summary" in report
    assert report["summary"]["total"] > 0