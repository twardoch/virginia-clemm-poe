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
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print(f"✅ {description} passed")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            if result.stdout.strip():
                print("STDOUT:", result.stdout)
            if result.stderr.strip():
                print("STDERR:", result.stderr)
            return False
            
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main() -> int:
    """Run all linting checks and return exit code."""
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    tests_path = project_root / "tests"
    
    # Change to project root
    import os
    os.chdir(project_root)
    
    print("🚀 Running comprehensive code quality checks...")
    print(f"Project root: {project_root}")
    
    checks = [
        # Code formatting and linting
        (["uvx", "ruff", "check", "src/", "tests/"], "Ruff linting"),
        (["uvx", "ruff", "format", "--check", "src/", "tests/"], "Ruff formatting"),
        
        # Type checking
        (["uvx", "mypy", "src/"], "MyPy type checking"),
        
        # Security scanning
        (["uvx", "bandit", "-r", "src/", "-c", "pyproject.toml"], "Bandit security check"),
        
        # Test execution with coverage
        (["uvx", "pytest", "tests/", "-m", "not integration", "--cov=virginia_clemm_poe", "--cov-report=term-missing"], "Unit tests with coverage"),
        
        # Documentation checks
        (["uvx", "pydocstyle", "src/", "--config=pyproject.toml"], "Docstring style check"),
    ]
    
    results = []
    
    for cmd, description in checks:
        success = run_command(cmd, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 LINT RESULTS SUMMARY")
    print("="*60)
    
    failed_checks = []
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} {description}")
        if not success:
            failed_checks.append(description)
    
    if failed_checks:
        print(f"\n❌ {len(failed_checks)} checks failed:")
        for check in failed_checks:
            print(f"   - {check}")
        print("\n💡 Fix the issues above and run the script again.")
        return 1
    else:
        print(f"\n🎉 All {len(results)} checks passed! Code is ready for commit.")
        return 0

if __name__ == "__main__":
    sys.exit(main())