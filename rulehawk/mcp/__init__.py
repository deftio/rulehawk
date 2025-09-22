"""
RuleHawk MCP (Model Context Protocol) Server

Allows AI assistants to interact with RuleHawk to:
- Discover project configuration
- Test commands to find what works
- Set up rules intelligently
- Run checks and get structured feedback
"""

try:
    from .server import RuleHawkMCPServer
    from .tools import (
        check_tool_installed,
        detect_project,
        find_test_runner,
        suggest_configuration,
        test_command,
    )

    __all__ = [
        "RuleHawkMCPServer",
        "detect_project",
        "test_command",
        "find_test_runner",
        "check_tool_installed",
        "suggest_configuration",
    ]
    MCP_AVAILABLE = True
except ImportError:
    # MCP dependencies not installed
    __all__ = []
    MCP_AVAILABLE = False
