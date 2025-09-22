"""Command verification system for RuleHawk."""

import logging
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of command verification."""

    safe: bool
    valid: bool = False
    reason: Optional[str] = None
    output_sample: Optional[str] = None
    duration_ms: Optional[int] = None
    files_modified: int = 0


class CommandVerifier:
    """Verify commands are safe and actually do what they claim."""

    # Dangerous command patterns to reject
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",  # Recursive force remove from root
        r"rm\s+-rf\s+~",  # Recursive force remove home
        r">\s*/dev/sd",  # Overwriting disk devices
        r"dd\s+if=.*of=/dev/",  # Direct disk write
        r"chmod\s+-R\s+777\s+/",  # Recursive permission change from root
        r"curl.*\|\s*sh",  # Pipe curl to shell
        r"wget.*\|\s*bash",  # Pipe wget to bash
        r":(){ :|:& };:",  # Fork bomb
        r"mkfs\.",  # Filesystem format
        r"rm\s+-rf\s+\*",  # Remove everything in current dir
        r">\s*/etc/",  # Overwriting system files
    ]

    # Command type validation rules
    COMMAND_VALIDATORS = {
        "test": {
            "must_contain": ["test", "spec", "check", "pytest", "jest", "mocha", "jasmine"],
            "must_not_contain": ["rm", "delete", "format", "install"],
            "expected_duration": (100, 300000),  # 0.1s to 5min
            "modifies_files": False,
            "expected_output_patterns": [r"test", r"pass", r"fail", r"ok", r"error"],
        },
        "lint": {
            "must_contain": ["lint", "check", "ruff", "flake", "eslint", "pylint", "rubocop"],
            "must_not_contain": ["rm", "delete", "install"],
            "expected_duration": (100, 60000),  # 0.1s to 1min
            "modifies_files": False,
            "expected_output_patterns": [
                r"error",
                r"warning",
                r"found",
                r"issue",
                r"problem",
                r"ok",
                r"clean",
            ],
        },
        "format": {
            "must_contain": ["format", "black", "prettier", "fmt", "autopep", "standard"],
            "must_not_contain": ["rm", "test", "install"],
            "expected_duration": (100, 60000),  # 0.1s to 1min
            "modifies_files": True,  # Formatters modify files
            "expected_output_patterns": [r"reformat", r"fixed", r"changed", r"modified"],
        },
        "coverage": {
            "must_contain": ["cov", "coverage", "cover"],
            "must_not_contain": ["rm", "delete", "install"],
            "expected_duration": (500, 600000),  # 0.5s to 10min
            "modifies_files": False,
            "expected_output_patterns": [r"\d+%", r"coverage", r"lines", r"statements"],
        },
        "build": {
            "must_contain": ["build", "compile", "bundle", "webpack", "rollup", "tsc"],
            "must_not_contain": ["rm -rf", "sudo"],
            "expected_duration": (500, 600000),  # 0.5s to 10min
            "modifies_files": True,
            "expected_output_patterns": [r"built", r"compiled", r"bundle", r"success", r"complete"],
        },
    }

    def __init__(self, project_root: Path):
        """Initialize verifier.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root

    def verify_command(self, command_type: str, command: str) -> VerificationResult:
        """Verify a command is safe and does what it claims.

        Args:
            command_type: Type of command (test, lint, format, etc.)
            command: Command string to verify

        Returns:
            VerificationResult with safety and validity information
        """
        # Step 1: Safety check
        if self.is_dangerous(command):
            return VerificationResult(safe=False, reason="Command contains dangerous patterns")

        # Step 2: Get validation rules for this command type
        validators = self.COMMAND_VALIDATORS.get(command_type.lower().replace("_cmd", ""))
        if not validators:
            # Unknown command type, be conservative
            validators = {
                "must_not_contain": ["rm", "delete", "sudo"],
                "expected_duration": (10, 600000),
                "modifies_files": False,
            }

        # Step 3: Basic validation
        validation_result = self._validate_against_rules(command, validators)
        if not validation_result.valid:
            return validation_result

        # Step 4: Dry run or sandbox execution
        execution_result = self._execute_sandboxed(command, validators)

        return execution_result

    def is_dangerous(self, command: str) -> bool:
        """Check if command contains dangerous patterns.

        Args:
            command: Command string to check

        Returns:
            True if dangerous patterns detected
        """
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected in command: {pattern}")
                return True
        return False

    def _validate_against_rules(self, command: str, validators: dict) -> VerificationResult:
        """Validate command against type-specific rules.

        Args:
            command: Command to validate
            validators: Validation rules

        Returns:
            VerificationResult
        """
        command_lower = command.lower()

        # Check for required keywords
        must_contain = validators.get("must_contain", [])
        if must_contain:
            if not any(keyword in command_lower for keyword in must_contain):
                return VerificationResult(
                    safe=True,
                    valid=False,
                    reason=f"Command doesn't appear to be a {' or '.join(must_contain)} command",
                )

        # Check for forbidden keywords
        must_not_contain = validators.get("must_not_contain", [])
        for forbidden in must_not_contain:
            if forbidden in command_lower:
                return VerificationResult(
                    safe=True,
                    valid=False,
                    reason=f"Command contains forbidden keyword: {forbidden}",
                )

        return VerificationResult(safe=True, valid=True)

    def _execute_sandboxed(self, command: str, validators: dict) -> VerificationResult:
        """Execute command in sandboxed way to verify behavior.

        Args:
            command: Command to execute
            validators: Validation rules including expected behavior

        Returns:
            VerificationResult with execution details
        """
        # Track files before execution
        files_before = self._get_file_snapshot()

        try:
            # Add dry-run flags if possible
            dry_run_command = self._add_dry_run_flags(command)

            # Execute with timeout
            start_time = time.time()
            result = subprocess.run(
                dry_run_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,  # 10 second timeout for verification
                cwd=self.project_root,
            )
            duration_ms = int((time.time() - start_time) * 1000)

            # Check output against expected patterns
            output = result.stdout + result.stderr
            output_sample = output[:500]  # First 500 chars

            # Check for expected output patterns
            expected_patterns = validators.get("expected_output_patterns", [])
            if expected_patterns:
                has_expected_output = any(
                    re.search(pattern, output, re.IGNORECASE) for pattern in expected_patterns
                )

                if not has_expected_output:
                    return VerificationResult(
                        safe=True,
                        valid=False,
                        reason="Output doesn't match expected patterns",
                        output_sample=output_sample,
                        duration_ms=duration_ms,
                    )

            # Check file modifications
            files_after = self._get_file_snapshot()
            files_modified = len(files_before.symmetric_difference(files_after))

            if not validators.get("modifies_files", False) and files_modified > 0:
                return VerificationResult(
                    safe=True,
                    valid=False,
                    reason=f"Command modified {files_modified} files when it shouldn't",
                    files_modified=files_modified,
                    duration_ms=duration_ms,
                )

            # Check duration is reasonable
            min_duration, max_duration = validators.get("expected_duration", (0, 600000))
            if duration_ms < min_duration:
                return VerificationResult(
                    safe=True,
                    valid=False,
                    reason="Command completed too quickly, might not be doing real work",
                    duration_ms=duration_ms,
                )
            elif duration_ms > max_duration:
                return VerificationResult(
                    safe=True,
                    valid=False,
                    reason="Command took too long, might be stuck",
                    duration_ms=duration_ms,
                )

            return VerificationResult(
                safe=True,
                valid=True,
                output_sample=output_sample,
                duration_ms=duration_ms,
                files_modified=files_modified,
            )

        except subprocess.TimeoutExpired:
            return VerificationResult(
                safe=True, valid=False, reason="Command timed out during verification"
            )
        except Exception as e:
            return VerificationResult(
                safe=True, valid=False, reason=f"Error during verification: {e}"
            )

    def _add_dry_run_flags(self, command: str) -> str:
        """Add dry-run flags to command if possible.

        Args:
            command: Original command

        Returns:
            Command with dry-run flags if applicable
        """
        # Common dry-run flags for various tools
        dry_run_mappings = {
            "pytest": "--collect-only",
            "ruff": "--no-fix",
            "black": "--check",
            "prettier": "--check",
            "eslint": "--no-fix",
            "npm test": "-- --listTests",
            "make": "-n",
            "cargo": "--dry-run",
        }

        for tool, flag in dry_run_mappings.items():
            if tool in command and flag not in command:
                # Add dry-run flag
                if " -- " in command:
                    # Command already has -- separator
                    return command.replace(" -- ", f" {flag} -- ")
                else:
                    # Add flag at the end
                    return f"{command} {flag}"

        return command

    def _get_file_snapshot(self) -> set:
        """Get snapshot of files in project.

        Returns:
            Set of file paths with modification times
        """
        snapshot = set()
        for path in self.project_root.rglob("*"):
            if path.is_file() and not any(p.startswith(".") for p in path.parts):
                try:
                    mtime = path.stat().st_mtime
                    snapshot.add(f"{path}:{mtime}")
                except:
                    pass
        return snapshot

    def verify_batch(self, commands: Dict[str, str]) -> Dict[str, VerificationResult]:
        """Verify multiple commands.

        Args:
            commands: Dictionary of command_type -> command

        Returns:
            Dictionary of command_type -> VerificationResult
        """
        results = {}
        for cmd_type, command in commands.items():
            logger.info(f"Verifying {cmd_type}: {command}")
            results[cmd_type] = self.verify_command(cmd_type, command)
        return results
