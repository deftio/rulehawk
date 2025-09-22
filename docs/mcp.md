# MCP (Model Context Protocol) Integration

## Overview

RuleHawk provides native MCP integration for AI agents, enabling structured communication and command learning through a well-defined protocol.

## What is MCP?

Model Context Protocol (MCP) is a standard for AI agents to interact with tools through structured APIs rather than text parsing. With MCP, agents can:
- Call functions directly
- Receive structured responses
- Teach RuleHawk commands
- Get real-time feedback

## Starting the MCP Server

### Interactive Mode (Recommended)
```bash
rulehawk mcp --interactive

# Output:
🦅 Starting Interactive RuleHawk MCP server on localhost:5173
✨ Agents can now teach me commands!
📚 Commands will be saved in rulehawk_data/ for future use
```

### Classic Mode
```bash
rulehawk mcp --classic

# Output:
🦅 Starting Classic RuleHawk MCP server on localhost:5173
AI assistants can now interact with RuleHawk
```

## MCP Tools Available

### Interactive Mode Tools

#### `ask_command`
RuleHawk asks for the right command to use.

**Request**:
```json
{
  "intent": "test",
  "context": {
    "language": "python",
    "files_found": ["test_*.py", "pytest.ini"]
  },
  "tried": ["pytest"],
  "question": "What command should I use for testing?"
}
```

**Response**:
```json
{
  "status": "need_answer",
  "suggestions": ["pytest", "uv run pytest", "python -m pytest"],
  "message": "Please provide the command to use"
}
```

#### `teach_command`
Agent teaches RuleHawk a command.

**Request**:
```json
{
  "intent": "test",
  "command": "uv run pytest",
  "save": true
}
```

**Response**:
```json
{
  "status": "learned",
  "command": "uv run pytest",
  "verified": true,
  "message": "Thanks! I'll use 'uv run pytest' for test"
}
```

#### `learn_project`
RuleHawk asks to learn about the project.

**Request**:
```json
{}
```

**Response**:
```json
{
  "status": "need_teaching",
  "detected": {
    "language": "python",
    "package_manager": "uv"
  },
  "questions": {
    "test": "What command runs tests?",
    "lint": "What command runs linting?",
    "format": "What command formats code?"
  }
}
```

#### `report_status`
RuleHawk reports check results.

**Request**:
```json
{
  "phase": "preflight",
  "passed": 3,
  "failed": 2,
  "failures": [
    {"rule": "A1", "issue": "Code not formatted"},
    {"rule": "P1", "issue": "Uncommitted changes"}
  ]
}
```

**Response**:
```json
{
  "summary": "3 passed, 2 failed",
  "options": ["fix_issues", "skip_failures", "abort"]
}
```

#### `run_command`
Execute a learned command.

**Request**:
```json
{
  "intent": "test"
}
```

**Response**:
```json
{
  "status": "success",
  "command": "uv run pytest",
  "exit_code": 0,
  "stdout": "All tests passed!"
}
```

### Classic Mode Tools

#### `detect_project`
Detect project type and configuration.

**Response**:
```json
{
  "language": "python",
  "framework": "django",
  "testing": {
    "framework": "pytest",
    "config_file": "pytest.ini"
  }
}
```

#### `test_command`
Test if a command works.

**Request**:
```json
{
  "command": "pytest --cov"
}
```

**Response**:
```json
{
  "success": true,
  "output": "test session starts...",
  "duration_ms": 1523
}
```

#### `validate_rules`
Validate a rules YAML configuration.

**Request**:
```json
{
  "yaml_content": "rules:\n  C1:\n    name: Zero Warnings..."
}
```

**Response**:
```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

## Agent Workflow Example

### First Time Setup

```python
# Agent connects to RuleHawk MCP
mcp = connect_to_rulehawk()

# RuleHawk asks to learn about project
response = mcp.learn_project()
# RuleHawk: "What command runs tests?"

# Agent teaches commands
mcp.teach_command({
    "intent": "test",
    "command": "npm test"
})
# RuleHawk: "Thanks! Verified and saved."

mcp.teach_command({
    "intent": "lint",
    "command": "npm run lint"
})
# RuleHawk: "Thanks! Verified and saved."
```

### Regular Development

```python
# Agent starts work
mcp.run_command({"intent": "preflight"})
# RuleHawk runs checks using learned commands

# Agent makes changes
edit_files()

# Before committing
result = mcp.run_command({"intent": "postflight"})
if result["status"] == "failed":
    fix_issues(result["failures"])
```

### Learning New Commands

```python
# RuleHawk encounters unknown command
response = mcp.ask_command({
    "intent": "coverage",
    "context": {"language": "javascript"}
})
# RuleHawk: "What command checks coverage?"

# Agent provides command
mcp.teach_command({
    "intent": "coverage",
    "command": "npm run test:coverage"
})
# RuleHawk: "Learned and verified!"
```

## Benefits of MCP Integration

### For AI Agents

1. **Structured Communication**
   - No text parsing required
   - Clear request/response format
   - Type-safe interactions

2. **Interactive Learning**
   - RuleHawk asks when it needs help
   - Agents teach commands once
   - Knowledge persists across sessions

3. **Reduced Token Usage**
   - Direct API calls vs CLI output parsing
   - Compact JSON responses
   - No need for verbose explanations

### For RuleHawk

1. **Command Discovery**
   - Learn project-specific commands
   - Verify commands actually work
   - Build confidence over time

2. **Safety**
   - Verify commands before trusting
   - Reject dangerous patterns
   - Audit all interactions

3. **Evolution**
   - Start with agent teaching
   - Progress to self-discovery
   - Eventually autonomous operation

## MCP Configuration

### Server Options

```bash
# Choose port
rulehawk mcp --port 8080

# Choose host
rulehawk mcp --host 0.0.0.0

# Classic mode (no learning)
rulehawk mcp --classic
```

### Client Connection

```python
# Python example
from mcp import Client

client = Client("http://localhost:5173")
result = client.call("learn_project", {})
```

```javascript
// JavaScript example
const mcp = new MCPClient("http://localhost:5173");
const result = await mcp.call("learn_project", {});
```

## Security Considerations

### Command Verification
All taught commands are verified before trust:
- Safety check for dangerous patterns
- Execution test to ensure they work
- Output validation for expected results

### Dangerous Patterns Rejected
```json
{
  "command": "rm -rf /",
  "status": "rejected",
  "reason": "Contains dangerous pattern"
}
```

### Audit Trail
All MCP interactions logged:
```jsonl
{"timestamp":"2024-01-20T10:30:00Z","event":"MCP_CALL","method":"teach_command","command":"npm test"}
{"timestamp":"2024-01-20T10:30:01Z","event":"VERIFY_CMD","command":"npm test","result":"safe"}
{"timestamp":"2024-01-20T10:30:02Z","event":"LEARN_CMD","command":"npm test","verified":true}
```

## Best Practices

### For Agent Developers

1. **Always verify responses**
   ```python
   response = mcp.teach_command(cmd)
   if response["status"] != "learned":
       handle_error(response["reason"])
   ```

2. **Use batch learning**
   ```python
   # Teach all commands at once
   for intent, command in commands.items():
       mcp.teach_command({
           "intent": intent,
           "command": command
       })
   ```

3. **Handle unknown commands gracefully**
   ```python
   result = mcp.run_command({"intent": "build"})
   if result["status"] == "unknown_command":
       # Teach the command
       mcp.teach_command({
           "intent": "build",
           "command": "npm run build"
       })
   ```

### For RuleHawk Integration

1. **Start with interactive mode** - Allows learning
2. **Commit learned commands** - Share with team
3. **Review audit logs** - Ensure correct learning
4. **Set confidence thresholds** - Require verification

## Troubleshooting

### MCP Server Won't Start

Check if MCP dependencies are installed:
```bash
pip install mcp
```

Check if port is already in use:
```bash
lsof -i :5173
```

### Commands Not Being Learned

Check the memory file:
```bash
cat rulehawk_data/rulehawk-cmd-learned.json
```

Check verification is passing:
```bash
grep VERIFY_CMD rulehawk_data/rulehawk-log.jsonl | tail
```

### Agent Can't Connect

Ensure server is running:
```bash
ps aux | grep "rulehawk mcp"
```

Check firewall settings:
```bash
# Allow local connections
sudo ufw allow 5173/tcp
```

## Future Enhancements

### Planned Features

1. **WebSocket support** - Real-time bidirectional communication
2. **Authentication** - Secure MCP endpoints
3. **Multi-agent consensus** - Vote on best commands
4. **Command discovery** - RuleHawk figures out commands itself

### Roadmap

- v0.2: Basic MCP with learning
- v0.3: WebSocket support
- v0.4: Built-in AI for discovery
- v0.5: Full autonomy

## Examples

### Complete Integration Example

```python
# Agent script with full RuleHawk integration
import mcp

class DevelopmentAgent:
    def __init__(self):
        self.rulehawk = mcp.Client("http://localhost:5173")
        self.setup_rulehawk()

    def setup_rulehawk(self):
        """Teach RuleHawk if needed"""
        result = self.rulehawk.call("get_memory_status")

        if not result["known_commands"]:
            # First time - teach commands
            self.rulehawk.call("teach_command", {
                "intent": "test",
                "command": "npm test"
            })
            self.rulehawk.call("teach_command", {
                "intent": "lint",
                "command": "npm run lint"
            })

    def develop(self, task):
        """Development workflow with RuleHawk"""
        # Preflight checks
        result = self.rulehawk.call("run_command", {
            "intent": "preflight"
        })
        if result["status"] != "success":
            self.fix_preflight_issues(result)

        # Do development work
        self.implement_feature(task)

        # Postflight checks
        result = self.rulehawk.call("run_command", {
            "intent": "postflight"
        })
        if result["status"] != "success":
            self.fix_postflight_issues(result)

        # Safe to commit
        self.commit_changes()
```

## Resources

- [MCP Specification](https://github.com/anthropics/mcp)
- [RuleHawk MCP Source](../rulehawk/mcp/)
- [Agent Workflow Guide](agent-workflow.md)
- [Interactive Learning](learning.md)