"""RuleHawk Memory System - Persistent command learning and storage."""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CommandEntry:
    """A learned command with metadata."""

    command: str
    learned_at: str
    learned_from: str
    verified: bool = False
    last_success: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.0
    verification: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Remove None values for cleaner JSON
        return {k: v for k, v in data.items() if v is not None}


class RuleHawkMemory:
    """Manages persistent memory for RuleHawk learned commands."""

    def __init__(self, project_root: Path):
        """Initialize memory system for a project.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.memory_dir = project_root / "rulehawk_data"
        self.memory_dir.mkdir(exist_ok=True)

        self.learned_file = self.memory_dir / "rulehawk-cmd-learned.json"
        self.log_file = self.memory_dir / "rulehawk-log.jsonl"

        self.learned_data = self._load_learned()

    def _load_learned(self) -> dict:
        """Load learned commands from JSON file."""
        if self.learned_file.exists():
            try:
                with open(self.learned_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse {self.learned_file}, starting fresh")
                return self._create_empty_learned()
        return self._create_empty_learned()

    def _create_empty_learned(self) -> dict:
        """Create empty learned commands structure."""
        return {
            "version": "1.0",
            "project_id": str(uuid.uuid4()),
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "last_updated_by": "unknown",
            "detected": {},
            "commands": {},
            "rejected_commands": [],
            "environment": {},
        }

    def save_learned(self, updated_by: str = "unknown"):
        """Save learned commands to JSON file.

        Args:
            updated_by: Identifier of who/what updated the commands
        """
        self.learned_data["last_updated"] = datetime.now().isoformat()
        self.learned_data["last_updated_by"] = updated_by

        with open(self.learned_file, "w") as f:
            json.dump(self.learned_data, f, indent=2)

        logger.info(f"Saved learned commands to {self.learned_file}")

    def log_event(self, event: str, **kwargs):
        """Append an event to the JSONL audit log.

        Args:
            event: Event type (e.g., "LEARN_CMD", "EXEC_CMD", "VERIFY_CMD")
            **kwargs: Additional event data
        """
        entry = {"timestamp": datetime.now().isoformat(), "event": event, **kwargs}

        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_command(self, cmd_type: str) -> Optional[str]:
        """Get a learned command if available and trusted.

        Args:
            cmd_type: Type of command (e.g., "TEST_CMD", "LINT_CMD")

        Returns:
            Command string if available and trusted, None otherwise
        """
        if cmd_type in self.learned_data["commands"]:
            cmd_data = self.learned_data["commands"][cmd_type]

            # Only return verified commands with decent confidence
            if cmd_data.get("verified") and cmd_data.get("confidence", 0) >= 0.7:
                self.log_event(
                    "USE_LEARNED_CMD",
                    type=cmd_type,
                    command=cmd_data["command"],
                    confidence=cmd_data["confidence"],
                )
                return cmd_data["command"]
        return None

    def learn_command(self, cmd_type: str, command: str, source: str):
        """Learn a new command (unverified).

        Args:
            cmd_type: Type of command (e.g., "TEST_CMD", "LINT_CMD")
            command: The command string to learn
            source: Who/what provided the command (e.g., "Claude-3.5")
        """
        self.learned_data["commands"][cmd_type] = {
            "command": command,
            "learned_at": datetime.now().isoformat(),
            "learned_from": source,
            "verified": False,
            "success_count": 0,
            "failure_count": 0,
            "confidence": 0.0,
            "needs_verification": True,
        }

        self.save_learned(source)
        self.log_event("LEARN_CMD", type=cmd_type, command=command, source=source, verified=False)

    def update_command_result(
        self,
        cmd_type: str,
        success: bool,
        duration_ms: Optional[int] = None,
        output_sample: Optional[str] = None,
    ):
        """Update command statistics based on execution result.

        Args:
            cmd_type: Type of command
            success: Whether the command succeeded
            duration_ms: Execution duration in milliseconds
            output_sample: Sample of command output
        """
        if cmd_type not in self.learned_data["commands"]:
            return

        cmd_data = self.learned_data["commands"][cmd_type]

        if success:
            cmd_data["success_count"] += 1
            cmd_data["last_success"] = datetime.now().isoformat()
            if duration_ms:
                cmd_data.setdefault("typical_duration_ms", duration_ms)
        else:
            cmd_data["failure_count"] += 1
            cmd_data["last_failure"] = datetime.now().isoformat()

        # Update confidence based on success/failure ratio
        cmd_data["confidence"] = self._calculate_confidence(cmd_data)

        self.save_learned()
        self.log_event(
            "EXEC_CMD",
            type=cmd_type,
            command=cmd_data["command"],
            result="success" if success else "failure",
            duration_ms=duration_ms,
            confidence=cmd_data["confidence"],
        )

    def _calculate_confidence(self, cmd_data: dict) -> float:
        """Calculate confidence score for a command.

        Args:
            cmd_data: Command data dictionary

        Returns:
            Confidence score between 0.0 and 1.0
        """
        success_count = cmd_data.get("success_count", 0)
        failure_count = cmd_data.get("failure_count", 0)
        total = success_count + failure_count

        if total == 0:
            return 0.0

        # Basic ratio with minimum trials requirement
        empirical = success_count / total

        # Require at least 3 successful runs for decent confidence
        if success_count < 3:
            empirical *= 0.5

        # Cap at 0.98 - never fully trust
        return min(empirical, 0.98)

    def mark_command_verified(
        self,
        cmd_type: str,
        verification_method: str,
        verification_details: Optional[Dict[str, Any]] = None,
    ):
        """Mark a command as verified after testing.

        Args:
            cmd_type: Type of command
            verification_method: How it was verified (e.g., "exit_code", "output_analysis")
            verification_details: Additional verification information
        """
        if cmd_type not in self.learned_data["commands"]:
            return

        cmd_data = self.learned_data["commands"][cmd_type]
        cmd_data["verified"] = True
        cmd_data["verification"] = {
            "method": verification_method,
            "verified_at": datetime.now().isoformat(),
            **(verification_details or {}),
        }

        # Boost confidence for verified commands
        cmd_data["confidence"] = max(cmd_data["confidence"], 0.7)

        self.save_learned()
        self.log_event(
            "VERIFY_CMD",
            type=cmd_type,
            command=cmd_data["command"],
            method=verification_method,
            result="verified",
        )

    def reject_command(self, command: str, suggested_by: str, reason: str):
        """Record a rejected command that didn't work or was dangerous.

        Args:
            command: The rejected command
            suggested_by: Who suggested it
            reason: Why it was rejected
        """
        rejection = {
            "command": command,
            "suggested_by": suggested_by,
            "rejected_at": datetime.now().isoformat(),
            "reason": reason,
        }

        self.learned_data.setdefault("rejected_commands", []).append(rejection)

        # Keep only last 50 rejections
        if len(self.learned_data["rejected_commands"]) > 50:
            self.learned_data["rejected_commands"] = self.learned_data["rejected_commands"][-50:]

        self.save_learned()
        self.log_event("REJECT_CMD", command=command, source=suggested_by, reason=reason)

    def get_all_commands(self) -> Dict[str, str]:
        """Get all learned commands that are verified.

        Returns:
            Dictionary of command_type -> command string
        """
        result = {}
        for cmd_type, cmd_data in self.learned_data.get("commands", {}).items():
            if cmd_data.get("verified") and cmd_data.get("confidence", 0) > 0.5:
                result[cmd_type] = cmd_data["command"]
        return result

    def set_project_info(
        self,
        language: str = None,
        framework: str = None,
        package_manager: str = None,
        test_framework: str = None,
    ):
        """Set detected project information.

        Args:
            language: Programming language
            framework: Framework (e.g., "django", "react")
            package_manager: Package manager (e.g., "uv", "npm")
            test_framework: Test framework (e.g., "pytest", "jest")
        """
        detected = self.learned_data.setdefault("detected", {})

        if language:
            detected["language"] = language
        if framework:
            detected["framework"] = framework
        if package_manager:
            detected["package_manager"] = package_manager
        if test_framework:
            detected["test_framework"] = test_framework

        self.save_learned()

    def get_project_info(self) -> dict:
        """Get detected project information.

        Returns:
            Dictionary of detected project information
        """
        return self.learned_data.get("detected", {})

    def clear_command(self, cmd_type: str):
        """Clear a learned command (for re-learning).

        Args:
            cmd_type: Type of command to clear
        """
        if cmd_type in self.learned_data["commands"]:
            del self.learned_data["commands"][cmd_type]
            self.save_learned()
            self.log_event("CLEAR_CMD", type=cmd_type)
