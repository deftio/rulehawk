"""
RuleHawk MCP (Model Context Protocol) Server

Allows AI assistants to interact with RuleHawk to:
- Discover project configuration
- Test commands to find what works
- Set up rules intelligently
- Run checks and get structured feedback
"""

from .server import RuleHawkMCPServer
from .tools import (
    detect_project,
    test_command,
    find_test_runner,
    check_tool_installed,
    suggest_configuration
)

__all__ = [
    'RuleHawkMCPServer',
    'detect_project',
    'test_command',
    'find_test_runner',
    'check_tool_installed',
    'suggest_configuration'
]