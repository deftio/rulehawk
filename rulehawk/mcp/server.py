"""
RuleHawk MCP Server implementation
"""

import json
import yaml
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from mcp import Server, Tool
from mcp.types import TextContent, ToolResult

from rulehawk.detection import detect_project
from .tools import (
    test_command as test_cmd,
    find_test_runner as find_runner,
    check_tool_installed as check_tool,
    suggest_configuration as suggest_config
)


class RuleHawkMCPServer:
    """MCP Server for RuleHawk - allows AI assistants to interact with RuleHawk"""
    
    def __init__(self):
        self.server = Server("rulehawk")
        self.project_root = Path.cwd()
        self._setup_tools()
    
    def _setup_tools(self):
        """Register all available tools"""
        
        @self.server.tool()
        async def detect_project() -> ToolResult:
            """Detect project type and configuration"""
            try:
                config = detect_project(self.project_root)
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps(config, indent=2)
                    )]
                )
            except Exception as e:
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error detecting project: {e}"
                    )],
                    is_error=True
                )
        
        @self.server.tool()
        async def test_command(command: str) -> ToolResult:
            """Test if a command works in the project"""
            try:
                result = await test_cmd(command, self.project_root)
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                )
            except Exception as e:
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error testing command: {e}"
                    )],
                    is_error=True
                )
        
        @self.server.tool()
        async def find_test_runner() -> ToolResult:
            """Find the test runner for this project"""
            try:
                runner_info = await find_runner(self.project_root)
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps(runner_info, indent=2)
                    )]
                )
            except Exception as e:
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error finding test runner: {e}"
                    )],
                    is_error=True
                )
        
        @self.server.tool()
        async def check_tool_installed(tool_name: str) -> ToolResult:
            """Check if a tool is installed"""
            try:
                result = await check_tool(tool_name)
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps({
                            "tool": tool_name,
                            "installed": result["installed"],
                            "path": result.get("path"),
                            "version": result.get("version")
                        }, indent=2)
                    )]
                )
            except Exception as e:
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error checking tool: {e}"
                    )],
                    is_error=True
                )
        
        @self.server.tool()
        async def suggest_configuration() -> ToolResult:
            """Suggest RuleHawk configuration for this project"""
            try:
                config = await suggest_config(self.project_root)
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=yaml.dump(config, default_flow_style=False)
                    )]
                )
            except Exception as e:
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error suggesting configuration: {e}"
                    )],
                    is_error=True
                )
        
        @self.server.tool()
        async def validate_rules(yaml_content: str) -> ToolResult:
            """Validate RuleHawk rules YAML"""
            try:
                import yaml
                rules = yaml.safe_load(yaml_content)
                
                # Basic validation
                errors = []
                warnings = []
                
                if not isinstance(rules, dict):
                    errors.append("Rules must be a dictionary")
                
                valid_phases = ['preflight', 'inflight', 'postflight', 'security', 'always']
                for phase in rules.get('phases', {}):
                    if phase not in valid_phases:
                        warnings.append(f"Unknown phase: {phase}")
                
                # Check each rule
                for phase, phase_rules in rules.get('phases', {}).items():
                    if not isinstance(phase_rules, list):
                        errors.append(f"Phase {phase} must contain a list of rules")
                        continue
                    
                    for i, rule in enumerate(phase_rules):
                        if 'id' not in rule:
                            errors.append(f"Rule {i} in {phase} missing 'id' field")
                        if 'description' not in rule:
                            warnings.append(f"Rule {rule.get('id', i)} missing description")
                        if 'type' not in rule:
                            errors.append(f"Rule {rule.get('id', i)} missing 'type' field")
                
                result = {
                    "valid": len(errors) == 0,
                    "errors": errors,
                    "warnings": warnings
                }
                
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                )
            except yaml.YAMLError as e:
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"YAML parse error: {e}"
                    )],
                    is_error=True
                )
            except Exception as e:
                return ToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error validating rules: {e}"
                    )],
                    is_error=True
                )
    
    async def run(self):
        """Run the MCP server"""
        async with self.server:
            await self.server.wait_for_shutdown()


if __name__ == "__main__":
    server = RuleHawkMCPServer()
    asyncio.run(server.run())