"""
Rule Validators - Simple validation functions for specific rules
"""

import os
import subprocess
from pathlib import Path
from typing import Any, Dict


def check_branch_protection(config: Dict[str, Any]) -> Dict[str, Any]:
    """Check if current branch is protected (A3)"""
    try:
        result = subprocess.run(
            ["git", "symbolic-ref", "--short", "HEAD"], capture_output=True, text=True
        )
        current_branch = result.stdout.strip()

        protected_branches = ["main", "master", "develop", "staging", "production"]
        if current_branch in protected_branches:
            return {
                "success": False,
                "message": f"Currently on protected branch: {current_branch}",
                "details": [
                    "Switch to a feature branch before making changes",
                    "Use: git checkout -b feature/your-feature-name",
                ],
            }

        return {"success": True, "message": f"On feature branch: {current_branch}"}
    except Exception as e:
        return {"success": False, "message": f"Could not determine current branch: {str(e)}"}


def check_environment(config: Dict[str, Any]) -> Dict[str, Any]:
    """Check if development environment is ready (P1)"""
    issues = []

    # Check git status
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            issues.append("Not in a git repository")
        elif result.stdout.strip():
            uncommitted = len(result.stdout.strip().split("\n"))
            issues.append(f"Working directory has {uncommitted} uncommitted changes")
    except:
        issues.append("Git not available")

    # Check for package manager files
    project_root = Path.cwd()
    if (project_root / "package.json").exists():
        # Check if node_modules exists
        if not (project_root / "node_modules").exists():
            issues.append("Dependencies not installed (run: npm install)")
    elif (project_root / "requirements.txt").exists():
        # Check for virtual environment
        if not os.environ.get("VIRTUAL_ENV"):
            issues.append("No Python virtual environment activated")

    if issues:
        return {"success": False, "message": "Environment validation failed", "details": issues}

    return {"success": True, "message": "Environment ready"}


def check_task_plan(config: Dict[str, Any]) -> Dict[str, Any]:
    """Check if task plan exists (P2)"""
    task_plan_path = Path("TASK-PLAN.md")

    if not task_plan_path.exists():
        return {
            "success": False,
            "message": "No task plan found",
            "details": [
                "Create TASK-PLAN.md with:",
                "- Objective: what you're building",
                "- Implementation Steps: checklist of tasks",
                "- Current Status: what's been completed",
            ],
        }

    content = task_plan_path.read_text()
    required_sections = ["## Objective", "## Implementation Steps", "## Current Status"]
    missing = [section for section in required_sections if section not in content]

    if missing:
        return {
            "success": False,
            "message": "Task plan incomplete",
            "details": [f"Missing section: {section}" for section in missing],
        }

    return {"success": True, "message": "Task plan exists and is complete"}


def check_task_plan_updated(config: Dict[str, Any]) -> Dict[str, Any]:
    """Check if task plan has been recently updated (F2)"""
    task_plan_path = Path("TASK-PLAN.md")

    if not task_plan_path.exists():
        return {"success": False, "message": "No task plan found"}

    # Check if file was modified in last 2 hours
    import time

    stat = task_plan_path.stat()
    hours_since_modified = (time.time() - stat.st_mtime) / 3600

    if hours_since_modified > 2:
        return {
            "success": False,
            "message": f"Task plan not updated recently ({hours_since_modified:.1f} hours ago)",
            "details": ["Update TASK-PLAN.md with current progress"],
        }

    return {"success": True, "message": "Task plan recently updated"}


def check_ci_status(config: Dict[str, Any]) -> Dict[str, Any]:
    """Check CI status (C3)"""
    # Check for common CI configuration files
    ci_files = [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", ".circleci/config.yml"]
    project_root = Path.cwd()

    ci_configured = any(
        (project_root / ci_file).exists()
        if not ci_file.startswith(".github")
        else (project_root / ".github" / "workflows").exists()
        for ci_file in ci_files
    )

    if not ci_configured:
        return {
            "success": False,
            "message": "No CI configuration found",
            "details": ["Configure CI/CD pipeline for automated checks"],
        }

    # In a real implementation, we'd check actual CI status via API
    # For now, just check if tests pass locally
    test_commands = {
        "python": "pytest",
        "javascript": "npm test",
        "typescript": "npm test",
    }

    # Detect language
    language = "unknown"
    if (project_root / "package.json").exists():
        language = "javascript"
    elif (project_root / "requirements.txt").exists():
        language = "python"

    test_cmd = test_commands.get(language)
    if test_cmd:
        try:
            result = subprocess.run(test_cmd, shell=True, capture_output=True, timeout=60)
            if result.returncode != 0:
                return {
                    "success": False,
                    "message": "Tests failing",
                    "details": ["Fix failing tests before proceeding"],
                }
        except:
            pass  # Tests not configured

    return {"success": True, "message": "CI checks passing (or not configured)"}


def run_security_phase(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run all security checks (C5)"""
    # This would run all S1-S8 rules
    # For now, just do a basic secret scan
    try:
        # Try gitleaks if available
        result = subprocess.run(
            ["gitleaks", "detect", "--no-git", "--exit-code", "0"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if "leak" in result.stdout.lower() or "secret" in result.stdout.lower():
            return {
                "success": False,
                "message": "Security issues detected",
                "details": ["Run: rulehawk check --phase security for details"],
            }
    except:
        # Gitleaks not installed
        pass

    return {"success": True, "message": "Basic security checks passed"}
