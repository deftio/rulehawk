"""
Base detector class for language/project detection
"""

import json
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class LanguageDetector(ABC):
    """Base class for language-specific project detection"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.config = {}

    @abstractmethod
    def detect(self) -> bool:
        """Check if this detector applies to the project"""
        pass

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """Analyze project and return configuration"""
        pass

    def check_tool_installed(self, command: str) -> bool:
        """Check if a command-line tool is installed"""
        try:
            # Try 'which' first (Unix-like systems)
            result = subprocess.run(["which", command], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return True

            # Try 'where' for Windows
            result = subprocess.run(["where", command], capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # Fallback: try running the command with --version
            try:
                result = subprocess.run(
                    [command, "--version"], capture_output=True, text=True, timeout=2
                )
                return result.returncode == 0
            except:
                return False

    def run_command(self, command: List[str]) -> Optional[str]:
        """Run a command and return output"""
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, cwd=self.project_root, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def find_files(self, pattern: str) -> List[Path]:
        """Find files matching pattern in project"""
        return list(self.project_root.glob(pattern))

    def read_json_file(self, filepath: Path) -> Optional[Dict]:
        """Safely read a JSON file with graceful error handling"""
        if not filepath.exists():
            return None

        try:
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else None
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {filepath}: {e}")
            return None
        except OSError as e:
            print(f"Warning: Could not read {filepath}: {e}")
            return None
        except Exception:
            return None

    def read_file_lines(self, filepath: Path, max_lines: int = 100) -> List[str]:
        """Read first N lines of a file with graceful error handling"""
        if not filepath.exists():
            return []

        try:
            lines = []
            with open(filepath, encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.strip())
            return lines
        except (OSError, UnicodeDecodeError) as e:
            # Log warning but don't crash
            print(f"Warning: Could not read {filepath}: {e}")
            return []
        except Exception:
            return []
