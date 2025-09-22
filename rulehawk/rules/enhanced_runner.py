"""
Enhanced Rule Runner with detailed failure reasons and skip functionality
"""

import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class RuleException:
    """Represents a rule exception/skip"""

    rule_id: str
    reason: str
    until_date: Optional[date] = None

    def is_active(self) -> bool:
        """Check if this exception is still active"""
        if self.until_date is None:
            return True
        return date.today() <= self.until_date


class RuleExceptionManager:
    """Manages rule exceptions from rulehawkignore file"""

    def __init__(self, ignore_file: Path = Path("rulehawkignore")):
        self.ignore_file = ignore_file
        self.exceptions = self._load_exceptions()

    def _load_exceptions(self) -> Dict[str, RuleException]:
        """Load exceptions from rulehawkignore file"""
        exceptions = {}

        if not self.ignore_file.exists():
            return exceptions

        try:
            with open(self.ignore_file) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Parse exception format
                    # Format: RULE_ID:reason or RULE_ID:until=YYYY-MM-DD:reason
                    parts = line.split(":", 2)
                    if len(parts) < 2:
                        print(f"Warning: Invalid exception format at line {line_num}: {line}")
                        continue

                    rule_id = parts[0].strip()

                    # Check for until date
                    if parts[1].startswith("until="):
                        try:
                            date_str = parts[1].replace("until=", "")
                            until_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                            reason = parts[2] if len(parts) > 2 else "Temporarily disabled"
                        except ValueError as e:
                            print(f"Warning: Invalid date at line {line_num}: {e}")
                            continue
                    else:
                        until_date = None
                        reason = ":".join(parts[1:])

                    exceptions[rule_id] = RuleException(rule_id, reason, until_date)

        except Exception as e:
            print(f"Warning: Could not load rulehawkignore: {e}")

        return exceptions

    def should_skip(self, rule_id: str) -> Tuple[bool, Optional[str]]:
        """Check if a rule should be skipped"""
        if rule_id in self.exceptions:
            exception = self.exceptions[rule_id]
            if exception.is_active():
                return True, exception.reason
            else:
                # Exception expired
                return False, f"Exception expired on {exception.until_date}"
        return False, None


class EnhancedRuleResult:
    """Enhanced result with detailed failure information"""

    def __init__(self, rule: Dict[str, Any]):
        self.rule_id = rule["id"]
        self.rule_name = rule["name"]
        self.severity = rule.get("severity", "info")
        self.phase = rule.get("phase", "unknown")
        self.description = rule.get("description", "")

        self.status = "unknown"
        self.message = ""
        self.details = []
        self.fix_available = False
        self.fix_command = None
        self.skip_reason = None
        self.command_output = None
        self.error_details = None

    def to_dict(self, verbosity: str = "normal") -> Dict[str, Any]:
        """Convert to dictionary with specified verbosity"""
        if verbosity == "minimal":
            return {
                "rule": self.rule_id,
                "status": self.status,
                "message": self.message[:100] if self.message else "",
            }

        result = {
            "rule": self.rule_id,
            "name": self.rule_name,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
        }

        if self.skip_reason:
            result["skip_reason"] = self.skip_reason

        if verbosity == "verbose":
            result["phase"] = self.phase
            result["description"] = self.description

            if self.details:
                result["details"] = self.details

            if self.fix_available:
                result["fix_available"] = True
                if self.fix_command:
                    result["fix_command"] = self.fix_command

            if self.command_output:
                result["command_output"] = self.command_output

            if self.error_details:
                result["error_details"] = self.error_details

        elif verbosity == "normal":
            if self.details:
                result["details"] = self.details[:3]  # First 3 details

            if self.fix_available:
                result["fixable"] = True

        return result


class EnhancedRuleRunner:
    """Enhanced rule runner with better error reporting and skip functionality"""

    def __init__(self, config: Dict[str, Any], verbosity: str = "normal"):
        self.config = config
        self.verbosity = verbosity
        self.exception_manager = RuleExceptionManager()
        self.project_root = Path.cwd()
        self.language = self._detect_language()

    def _detect_language(self) -> str:
        """Detect the primary language of the project"""
        if (self.project_root / "package.json").exists():
            if (self.project_root / "tsconfig.json").exists():
                return "typescript"
            return "javascript"
        elif (
            (self.project_root / "requirements.txt").exists()
            or (self.project_root / "pyproject.toml").exists()
            or (self.project_root / "setup.py").exists()
        ):
            return "python"
        return "unknown"

    def check_rules(self, rules: List[Dict[str, Any]], auto_fix: bool = False) -> Dict[str, Any]:
        """Check multiple rules with enhanced reporting"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "verbosity": self.verbosity,
            "total_count": len(rules),
            "passed_count": 0,
            "failed_count": 0,
            "skipped_count": 0,
            "warning_count": 0,
            "details": [],
        }

        for rule in rules:
            result = self._check_single_rule(rule, auto_fix)
            results["details"].append(result.to_dict(self.verbosity))

            if result.status == "passed":
                results["passed_count"] += 1
            elif result.status == "skipped":
                results["skipped_count"] += 1
            elif result.status == "failed":
                if result.severity in ("warning", "info"):
                    results["warning_count"] += 1
                else:
                    results["failed_count"] += 1

        return results

    def _check_single_rule(self, rule: Dict[str, Any], auto_fix: bool) -> EnhancedRuleResult:
        """Check a single rule with enhanced error reporting"""
        result = EnhancedRuleResult(rule)

        # Check if rule should be skipped
        should_skip, skip_reason = self.exception_manager.should_skip(rule["id"])
        if should_skip:
            result.status = "skipped"
            result.message = f"Skipped: {skip_reason}"
            result.skip_reason = skip_reason
            return result

        try:
            # Check for language-specific command
            check_command = None
            if isinstance(rule.get("check_command"), dict):
                check_command = rule["check_command"].get(self.language)
            elif isinstance(rule.get("check_command"), str):
                check_command = rule["check_command"]

            if check_command:
                # Run the check command
                try:
                    proc_result = subprocess.run(
                        check_command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=self.project_root,
                    )

                    result.command_output = {
                        "stdout": proc_result.stdout[:500] if self.verbosity == "verbose" else None,
                        "stderr": proc_result.stderr[:500] if proc_result.stderr else None,
                        "return_code": proc_result.returncode,
                    }

                    if proc_result.returncode == 0:
                        result.status = "passed"
                        result.message = "Check completed successfully"
                    else:
                        result.status = "failed"
                        result.message = self._extract_error_message(
                            proc_result.stderr or proc_result.stdout
                        )
                        result.details = self._extract_error_details(
                            proc_result.stderr or proc_result.stdout
                        )

                        # Check if fix is available
                        if rule.get("fix_command"):
                            result.fix_available = True
                            fix_cmd = rule["fix_command"]
                            if isinstance(fix_cmd, dict):
                                result.fix_command = fix_cmd.get(self.language)
                            else:
                                result.fix_command = fix_cmd

                except subprocess.TimeoutExpired:
                    result.status = "failed"
                    result.message = "Check timed out after 30 seconds"
                    result.error_details = "Command took too long to execute"

                except Exception as e:
                    result.status = "failed"
                    result.message = f"Error running check: {str(e)}"
                    result.error_details = str(e)
            else:
                # No check command available
                result.status = "unknown"
                result.message = f"No check command available for {self.language}"

        except Exception as e:
            result.status = "error"
            result.message = f"Unexpected error: {str(e)}"
            result.error_details = str(e)

        return result

    def _extract_error_message(self, output: str) -> str:
        """Extract meaningful error message from command output"""
        if not output:
            return "Check failed with no output"

        lines = output.strip().split("\n")

        # Look for common error patterns
        for line in lines:
            if "error:" in line.lower() or "failed:" in line.lower():
                return line.strip()

        # Return first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()

        return "Check failed"

    def _extract_error_details(self, output: str) -> List[str]:
        """Extract detailed error information"""
        if not output:
            return []

        details = []
        lines = output.strip().split("\n")

        # Look for file:line:column patterns (common in linters)
        file_pattern = re.compile(r"^(.+):(\d+):(\d+):\s*(.+)$")

        for line in lines[:10]:  # Limit to first 10 lines
            match = file_pattern.match(line)
            if match:
                details.append(f"{match.group(1)}:{match.group(2)} - {match.group(4)}")
            elif line.strip() and not line.startswith(" "):
                details.append(line.strip())

        return details[:5]  # Return max 5 details
