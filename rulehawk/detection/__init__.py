"""
Project detection system for RuleHawk
"""

from pathlib import Path
from typing import Any, Dict

from .cpp_detector import CppDetector
from .javascript_detector import JavaScriptDetector
from .python_detector import PythonDetector


def detect_project(project_root: Path = None) -> Dict[str, Any]:
    """
    Detect project type and configuration

    Args:
        project_root: Project root directory (defaults to current directory)

    Returns:
        Dictionary with project configuration
    """
    if project_root is None:
        project_root = Path.cwd()

    detectors = [
        PythonDetector(project_root),
        JavaScriptDetector(project_root),
        CppDetector(project_root),
    ]

    for detector in detectors:
        if detector.detect():
            return detector.analyze()

    # Fallback - unknown project type
    return {
        "language": "unknown",
        "message": "Could not detect project type",
        "suggestions": [
            "Add a package.json for JavaScript/TypeScript",
            "Add a setup.py or pyproject.toml for Python",
            "Add a Makefile or CMakeLists.txt for C/C++",
        ],
    }


__all__ = ["detect_project", "PythonDetector", "JavaScriptDetector", "CppDetector"]
