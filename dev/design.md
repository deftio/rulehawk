# RuleHawk Design & Architecture

## Vision

RuleHawk evolves from a simple rule enforcer to an **autonomous command orchestrator** that:
1. Learns commands once (from any agent)
2. Remembers them permanently
3. Executes them reliably
4. Eventually figures them out itself

The key paradigm shift: **RuleHawk asks agents for commands rather than trying to detect them**.

## Architecture Evolution

### Stage 1: Agent-Taught (Current)
```
Agent → RuleHawk: "Use 'uv run pytest' for tests"
RuleHawk: *learns and saves* "OK, I'll remember that"
```

### Stage 2: Self-Learning (Near Future)
```
RuleHawk: *sees pytest.ini and .venv/*
RuleHawk: *tries variations automatically*
RuleHawk: "Found working command: uv run pytest"
```

### Stage 3: AI-Powered (Future)
```
RuleHawk AI: *analyzes project structure*
RuleHawk AI: "This looks like a Django project with custom test runner"
RuleHawk AI: "Discovered command: python manage.py test --parallel"
```

## Directory Structure

```
project-root/
├── rulehawk.yaml                    # Rules to enforce (committed)
├── rulehawk/                       # RuleHawk's working directory (committed)
│   ├── rulehawk-cmd-learned.json   # Learned commands (committed)
│   └── rulehawk-log.jsonl          # Audit log (committed)
└── rulehawkignore                  # Rule exceptions (committed)
```

### Why Everything is Committed
- New team member clones repo → RuleHawk immediately knows all commands
- Git tracks command evolution
- Shared knowledge between agents
- Complete audit trail

## Memory System

### Learned Commands Format
```json
{
  "version": "1.0",
  "commands": {
    "TEST_CMD": {
      "command": "uv run pytest",
      "learned_from": "Claude-3.5",
      "verified": true,
      "confidence": 0.93,
      "success_count": 25,
      "failure_count": 2
    }
  },
  "rejected_commands": [
    {
      "command": "echo 'tests pass'",
      "reason": "No actual test execution detected"
    }
  ]
}
```

### Trust & Verification Model

1. **Command Verification**
   - Safety checks (no dangerous patterns like `rm -rf /`)
   - Behavioral validation (test commands should mention "test" or "pass")
   - Output analysis (commands should produce expected output)

2. **Confidence Scoring**
   - Starts at 0.0 for new commands
   - Increases with successful executions
   - Decreases more aggressively with failures
   - Commands need >0.7 confidence to be trusted

3. **Audit Trail** (JSONL format)
   ```jsonl
   {"timestamp":"2024-01-20T10:30:00Z","event":"LEARN_CMD","type":"TEST_CMD","command":"uv run pytest","source":"Claude-3.5"}
   {"timestamp":"2024-01-20T10:30:15Z","event":"EXEC_CMD","result":"success","duration_ms":1523}
   ```

## MCP Integration

### Interactive Learning Flow

Instead of RuleHawk trying to detect commands, it asks agents through MCP:

```python
# RuleHawk asks for help
mcp.ask_command({
    "intent": "test",
    "context": {
        "language": "python",
        "files_found": ["pytest.ini", "test_*.py"]
    },
    "question": "What command should I use for testing?"
})

# Agent responds
{
    "command": "uv run pytest",
    "save_for_future": true
}
```

### MCP Tools

1. **ask_command** - Get the right command for an intent
2. **report_status** - Report check results and ask for guidance
3. **learn_project** - Initial setup conversation
4. **track_changes** - Focus checks based on what changed

### Future State: Agents Just Call High-Level Operations

```python
# Agent doesn't need to know ANY commands
class Agent:
    def develop(self):
        rulehawk.preflight()     # RuleHawk knows how
        self.edit_code()
        rulehawk.inflight()      # RuleHawk handles it
        rulehawk.postflight()    # RuleHawk does it all
        rulehawk.commit("Fix: Issue #123")
```

## Command Discovery Intelligence

### Pattern Recognition
```python
def discover_test_command(self, project_context):
    # Check for common patterns
    if Path("pytest.ini").exists():
        base = "pytest"
    elif Path("manage.py").exists():
        base = "python manage.py test"

    # Try intelligent variations
    variations = [
        base,
        f"uv run {base}",
        f"poetry run {base}",
        f".venv/bin/{base}"
    ]

    # Test each until one works
    for cmd in variations:
        if self.verify_works(cmd):
            return cmd
```

### Context-Aware Execution
```python
# Different commands for different contexts
if self.in_github_action():
    return "pytest --cov --junit-xml=results.xml"
elif self.in_pre_commit():
    return "pytest tests/unit -x"  # Fast subset
else:
    return "pytest -v"  # Full local test
```

## Release Strategy

### Alpha Release (0.1.0)
- Core rule checking works
- Basic command learning via MCP
- Manual command configuration

### Beta Release (0.2.0)
- Persistent memory system
- Trust verification
- Interactive MCP fully functional

### 1.0 Release
- Self-discovery of common commands
- Multi-agent consensus
- Production-ready

## Key Design Decisions

1. **Ask, Don't Detect** - Agents know their tools better than we can detect
2. **Trust but Verify** - Check commands actually do what they claim
3. **Persistent Memory** - Commands survive across sessions via rulehawk/
4. **Progressive Enhancement** - Works without MCP, better with it
5. **Git-Native** - All configuration is version controlled

## Project Integration Strategy

### The Key Innovation
RuleHawk generates project-native scripts that call it, so agents use familiar commands:

```bash
# Instead of agents learning:
rulehawk preflight --output yaml

# They just use:
npm run preflight  # For Node.js projects
make preflight     # For Python/Make projects
cargo preflight    # For Rust projects
```

### Integration Flow
1. **Agent reads rulehawk.yaml** - Sees integration instructions
2. **Runs `rulehawk integrate --write`** - Creates project scripts
3. **Uses standard commands** - npm run, make, cargo, etc.
4. **RuleHawk enforces rules** - Transparently in background

### Generated Scripts
- **package.json** - Adds npm run scripts
- **Makefile** - Adds make targets
- **.cargo/config.toml** - Adds cargo aliases
- **Git hooks** - Pre-commit/pre-push checks

## Implementation Status

✅ Completed:
- Basic rule checking
- Enhanced error reporting
- rulehawkignore support
- Memory system class (RuleHawkMemory)
- Command verification system (CommandVerifier)
- Interactive MCP server
- Project integration generator

🚧 In Progress:
- Testing and refinement
- Documentation

📋 Planned:
- Self-discovery patterns
- Built-in AI for command detection
- Multi-agent consensus

## Why This Architecture Works

1. **Single Source of Truth** - RuleHawk owns all command knowledge
2. **No Duplication** - Agents don't each learn the same commands
3. **Consistency** - All agents use the same commands
4. **Evolution** - RuleHawk gets smarter over time
5. **Simplicity** - Agents just call high-level operations

## Security Considerations

- Dangerous command patterns are rejected
- Commands are verified before trusting
- All actions are logged for audit
- Confidence scoring prevents bad commands from persisting
- Time limits prevent runaway processes

## The End Goal

RuleHawk becomes the intelligent layer between agents and projects:
- Agents don't need to know project-specific commands
- RuleHawk handles all the complexity
- Projects get consistent, reliable automation
- Knowledge accumulates and improves over time