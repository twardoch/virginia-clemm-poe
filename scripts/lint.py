#!/usr/bin/env python3
"""Local linting script for comprehensive code quality checks.

This script runs all the linting tools configured for the project,
providing a single command to validate code quality before committing.
"""

import subprocess
import sys
from pathlib import Path

# this_file: scripts/lint.py


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            if result.stdout.strip():
                pass
            return True
        if result.stdout.strip():
            pass
        if result.stderr.strip():
            pass
        return False

    except FileNotFoundError:
        return False
    except Exception:
        return False


def main() -> int:
    """Run all linting checks and return exit code."""
    project_root = Path(__file__).parent.parent
    project_root / "src"
    project_root / "tests"

    # Change to project root
    import os

    os.chdir(project_root)

    checks = [
        # Code formatting and linting
        (["uvx", "ruff", "check", "src/", "tests/"], "Ruff linting"),
        (["uvx", "ruff", "format", "--check", "src/", "tests/"], "Ruff formatting"),
        # Type checking
        (["uvx", "mypy", "src/"], "MyPy type checking"),
        # Security scanning
        (["uvx", "bandit", "-r", "src/", "-c", "pyproject.toml"], "Bandit security check"),
        # Test execution with coverage
        (
            [
                "uvx",
                "pytest",
                "tests/",
                "-m",
                "not integration",
                "--cov=virginia_clemm_poe",
                "--cov-report=term-missing",
            ],
            "Unit tests with coverage",
        ),
        # Documentation checks
        (["uvx", "pydocstyle", "src/", "--config=pyproject.toml"], "Docstring style check"),
    ]

    results = []

    for cmd, description in checks:
        success = run_command(cmd, description)
        results.append((description, success))

    # Summary

    failed_checks = []
    for description, success in results:
        if not success:
            failed_checks.append(description)

    if failed_checks:
        for _check in failed_checks:
            pass
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
