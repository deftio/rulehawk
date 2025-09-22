"""Interactive MCP Server for RuleHawk - Learns from agents."""

import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..detection import detect_project
from ..memory import RuleHawkMemory
from ..verifier import CommandVerifier

# Try to import MCP dependencies
MCP_AVAILABLE = False
try:
    from mcp import Server, Tool
    from mcp.types import TextContent, ToolResult

    MCP_AVAILABLE = True
except ImportError:
    # Stub classes if MCP not available
    class Server:
        def __init__(self, *args, **kwargs):
            pass

    class Tool:
        def __init__(self, *args, **kwargs):
            pass

    class TextContent:
        def __init__(self, *args, **kwargs):
            self.text = kwargs.get("text", "")
            self.type = kwargs.get("type", "text")

    class ToolResult:
        def __init__(self, *args, **kwargs):
            self.content = kwargs.get("content", [])
            self.is_error = kwargs.get("is_error", False)


logger = logging.getLogger(__name__)


class InteractiveRuleHawkMCP:
    """Interactive MCP server where RuleHawk asks agents for help."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the interactive MCP server.

        Args:
            project_root: Project root path (defaults to current directory)
        """
        self.server = Server("rulehawk-interactive")
        self.project_root = project_root or Path.cwd()
        self.memory = RuleHawkMemory(self.project_root)
        self.verifier = CommandVerifier(self.project_root)
        self._setup_tools()

    def _setup_tools(self):
        """Register interactive MCP tools."""

        @self.server.tool()
        async def ask_command(request: Dict[str, Any]) -> ToolResult:
            """RuleHawk asks agent for the right command.

            Args:
                request: {
                    "intent": "test|lint|format|coverage|build",
                    "context": {...},
                    "tried": ["commands", "that", "failed"],
                    "question": "What command should I use?"
                }

            Returns:
                ToolResult with agent's response
            """
            # Check if we already know this command
            cmd_type = f"{request['intent'].upper()}_CMD"
            existing = self.memory.get_command(cmd_type)

            if existing:
                return ToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "already_known",
                                    "command": existing,
                                    "message": f"I already know to use: {existing}",
                                },
                                indent=2,
                            ),
                        )
                    ]
                )

            # RuleHawk needs help
            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "status": "need_answer",
                                "question": request.get("question"),
                                "context": request.get("context"),
                                "suggestions": self._get_command_suggestions(request["intent"]),
                                "message": "Please provide the command to use",
                            },
                            indent=2,
                        ),
                    )
                ]
            )

        @self.server.tool()
        async def teach_command(request: Dict[str, Any]) -> ToolResult:
            """Agent teaches RuleHawk a command.

            Args:
                request: {
                    "intent": "test|lint|format|coverage|build",
                    "command": "uv run pytest",
                    "save": true
                }

            Returns:
                ToolResult with verification status
            """
            intent = request["intent"]
            command = request["command"]
            cmd_type = f"{intent.upper()}_CMD"

            # Verify the command is safe and works
            verification = self.verifier.verify_command(intent, command)

            if not verification.safe:
                self.memory.reject_command(command, "agent", verification.reason)
                return ToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "rejected",
                                    "reason": verification.reason,
                                    "message": "Command rejected for safety reasons",
                                },
                                indent=2,
                            ),
                        )
                    ]
                )

            if not verification.valid:
                self.memory.reject_command(command, "agent", verification.reason)
                return ToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "invalid",
                                    "reason": verification.reason,
                                    "message": "Command doesn't appear to work correctly",
                                },
                                indent=2,
                            ),
                        )
                    ]
                )

            # Command is good! Learn it
            if request.get("save", True):
                self.memory.learn_command(cmd_type, command, "agent")
                self.memory.mark_command_verified(
                    cmd_type, "agent_provided", {"duration_ms": verification.duration_ms}
                )

            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "status": "learned",
                                "command": command,
                                "verified": True,
                                "duration_ms": verification.duration_ms,
                                "message": f"Thanks! I'll use '{command}' for {intent}",
                            },
                            indent=2,
                        ),
                    )
                ]
            )

        @self.server.tool()
        async def learn_project(request: Dict[str, Any] = None) -> ToolResult:
            """RuleHawk asks agent to teach it about the project.

            Returns:
                ToolResult with questions for the agent
            """
            # Detect what we can
            if request is None:
                request = {}
            detected = detect_project()
            self.memory.set_project_info(**detected)

            # See what we already know
            known_commands = self.memory.get_all_commands()

            # Figure out what we need to learn
            needed = []
            for cmd_type in ["TEST_CMD", "LINT_CMD", "FORMAT_CMD", "COVERAGE_CMD", "BUILD_CMD"]:
                if cmd_type not in known_commands:
                    needed.append(cmd_type.replace("_CMD", "").lower())

            if not needed:
                return ToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "already_configured",
                                    "known_commands": known_commands,
                                    "message": "I already know all the commands for this project!",
                                },
                                indent=2,
                            ),
                        )
                    ]
                )

            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "status": "need_teaching",
                                "detected": detected,
                                "known_commands": known_commands,
                                "questions": {
                                    cmd: f"What command should I use for {cmd}?" for cmd in needed
                                },
                                "message": "Please teach me these commands for your project",
                            },
                            indent=2,
                        ),
                    )
                ]
            )

        @self.server.tool()
        async def report_status(request: Dict[str, Any]) -> ToolResult:
            """RuleHawk reports check results and asks for guidance.

            Args:
                request: {
                    "phase": "preflight|postflight",
                    "passed": 3,
                    "failed": 2,
                    "failures": [...],
                    "question": "How should I proceed?"
                }

            Returns:
                ToolResult with status report
            """
            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "phase": request["phase"],
                                "summary": f"{request['passed']} passed, {request['failed']} failed",
                                "failures": request.get("failures", []),
                                "question": request.get("question", "How should I proceed?"),
                                "options": [
                                    "fix_issues",
                                    "skip_failures",
                                    "add_exceptions",
                                    "abort",
                                ],
                            },
                            indent=2,
                        ),
                    )
                ]
            )

        @self.server.tool()
        async def run_command(request: Dict[str, Any]) -> ToolResult:
            """Run a learned command.

            Args:
                request: {
                    "intent": "test|lint|format|coverage|build"
                }

            Returns:
                ToolResult with execution result
            """
            intent = request["intent"]
            cmd_type = f"{intent.upper()}_CMD"

            # Get the learned command
            command = self.memory.get_command(cmd_type)

            if not command:
                return ToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "unknown_command",
                                    "message": f"I don't know how to {intent} yet. Please teach me first.",
                                },
                                indent=2,
                            ),
                        )
                    ]
                )

            # Execute the command
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    cwd=self.project_root,
                )

                success = result.returncode == 0
                self.memory.update_command_result(cmd_type, success)

                return ToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "success" if success else "failure",
                                    "command": command,
                                    "exit_code": result.returncode,
                                    "stdout": result.stdout[-1000:] if result.stdout else "",
                                    "stderr": result.stderr[-1000:] if result.stderr else "",
                                },
                                indent=2,
                            ),
                        )
                    ]
                )

            except subprocess.TimeoutExpired:
                self.memory.update_command_result(cmd_type, False)
                return ToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "timeout",
                                    "command": command,
                                    "message": "Command timed out after 5 minutes",
                                },
                                indent=2,
                            ),
                        )
                    ]
                )
            except Exception as e:
                self.memory.update_command_result(cmd_type, False)
                return ToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {"status": "error", "command": command, "error": str(e)}, indent=2
                            ),
                        )
                    ]
                )

        @self.server.tool()
        async def get_memory_status() -> ToolResult:
            """Get current memory status - what RuleHawk knows.

            Returns:
                ToolResult with memory information
            """
            return ToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "project_info": self.memory.get_project_info(),
                                "known_commands": self.memory.get_all_commands(),
                                "learned_file": str(self.memory.learned_file),
                                "message": "This is what I know about the project",
                            },
                            indent=2,
                        ),
                    )
                ]
            )

    def _get_command_suggestions(self, intent: str) -> List[str]:
        """Get command suggestions based on intent and project.

        Args:
            intent: Command intent (test, lint, etc.)

        Returns:
            List of suggested commands
        """
        project_info = self.memory.get_project_info()
        language = project_info.get("language", "")

        suggestions = {
            "test": {
                "python": ["pytest", "python -m pytest", "uv run pytest", "python -m unittest"],
                "javascript": ["npm test", "yarn test", "jest", "mocha"],
                "rust": ["cargo test"],
                "go": ["go test ./..."],
                "java": ["mvn test", "gradle test"],
            },
            "lint": {
                "python": ["ruff check .", "pylint", "flake8", "uv run ruff check ."],
                "javascript": ["eslint .", "npm run lint", "standard"],
                "rust": ["cargo clippy"],
                "go": ["golangci-lint run"],
                "java": ["mvn checkstyle:check"],
            },
            "format": {
                "python": ["black .", "ruff format .", "autopep8", "uv run black ."],
                "javascript": ["prettier --write .", "npm run format"],
                "rust": ["cargo fmt"],
                "go": ["go fmt ./...", "gofumpt -w ."],
                "java": ["mvn formatter:format"],
            },
        }

        return suggestions.get(intent, {}).get(language, [])

    async def run(self):
        """Run the interactive MCP server."""
        if not MCP_AVAILABLE:
            logger.error("MCP dependencies not available")
            return

        async with self.server:
            await self.server.wait_for_shutdown()


def main():
    """Run the interactive MCP server."""
    server = InteractiveRuleHawkMCP()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
