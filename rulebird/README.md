# RuleBird 🦉

Lightweight rule enforcement CLI for codebases - perfect for humans and AI agents alike!

```
    ___
   (o,o)    RuleBird v0.1.0
  <  .  >   Keeping your code in check
   -=--
```

## Why RuleBird?

When working with AI coding agents (Claude, Cursor, OpenAI, etc.), ensuring consistent code quality becomes challenging. Agents might forget rules, miss context, or have rules float out of their context window.

**RuleBird solves this by providing a simple, reliable external tool that agents can call to check and enforce rules.**

Instead of asking agents to remember complex rules, they just need to remember one thing: `rulebird check`

## Features

- 🚀 **Lightweight** - No heavy dependencies, fast execution
- 🤖 **AI-Friendly** - Simple commands perfect for coding agents
- 🔌 **Extensible** - Integrate with any AI provider or tool
- 📋 **Comprehensive** - Covers security, testing, formatting, and more
- 🎯 **Phased Checks** - Preflight, inflight, postflight validation
- 🔧 **Auto-Fix** - Automatically fix what can be fixed
- 📊 **Audit Trail** - Every check is logged for compliance

## Quick Start

### Installation

```bash
# Install from PyPI (coming soon)
pip install rulebird

# Or install from source
git clone https://github.com/deftio/rulebird.git
cd rulebird
pip install -e .
```

### Initialize in Your Project

```bash
cd your-project
rulebird init
```

This creates `.rulebird.yaml` with sensible defaults.

### Basic Usage

```bash
# Check all rules
rulebird check

# Check specific phase
rulebird check --phase preflight    # Before starting work
rulebird check --phase postflight   # Before committing

# Check specific rules
rulebird check S1 S2   # Check security rules S1 and S2

# Auto-fix issues
rulebird check --fix

# Enforce rules (exit with error if any fail)
rulebird check --enforce
```

## For AI Agents

### Simple Workflow for Agents

1. **Before starting work:**
   ```bash
   rulebird preflight
   ```

2. **During development (optional):**
   ```bash
   rulebird check --phase inflight
   ```

3. **Before committing:**
   ```bash
   rulebird postflight
   ```

### Integration Example

When instructing an AI agent:

```
Before you start coding, run `rulebird preflight` to ensure the environment is ready.
After making changes, run `rulebird postflight` to verify all rules pass.
If any rules fail, fix them before proceeding.
```

### JSON Output for Parsing

```bash
# Get machine-readable output
rulebird check --json

# Output:
{
  "total_count": 15,
  "passed_count": 13,
  "failed_count": 2,
  "details": [
    {
      "rule_id": "S1",
      "status": "failed",
      "message": "Hardcoded secret detected",
      "details": ["api_key found in config.py:45"]
    }
  ]
}
```

## Rule Categories

### Security Rules (S1-S8)
- **S1**: No hardcoded secrets
- **S2**: Secure credential storage
- **S3**: Authentication best practices
- **S4**: Input validation
- **S5**: Dependency security
- **S6**: Secure communication
- **S7**: Logging security
- **S8**: Security testing

### Always-Active Rules (A1-A3)
- **A1**: Code formatting
- **A2**: Organize experimental files
- **A3**: Branch protection

### Preflight Rules (P1-P2)
- **P1**: Environment validation
- **P2**: Task planning

### In-Flight Rules (F1-F3)
- **F1**: Document public APIs
- **F2**: Update task plan
- **F3**: Test as you go

### Post-Flight Rules (C1-C5)
- **C1**: Zero warnings
- **C2**: Test coverage
- **C3**: CI must be green
- **C4**: Documentation complete
- **C5**: Security review

## Configuration

### Basic Configuration (.rulebird.yaml)

```yaml
# AI provider for complex checks
ai_provider: claude  # or: openai, cursor, local, none

# Phases to run by default
enabled_phases:
  - preflight
  - postflight
  - security

# Specific rules to enable (or 'all')
enabled_rules: all

# Paths to ignore
ignore_paths:
  - node_modules/
  - .venv/
  - vendor/

# Tool configuration
tools:
  python:
    formatter: ruff
    linter: ruff
    security: bandit
  javascript:
    formatter: prettier
    linter: eslint
```

### Environment Variables

```bash
export RULEBIRD_AI_PROVIDER=claude
export RULEBIRD_LOG_DIR=.logs
export OPENAI_API_KEY=your-key  # For OpenAI provider
```

## AI Provider Integration

RuleBird can use AI providers for complex rule checking:

### Claude Integration

```bash
# Ensure Claude CLI is installed
rulebird check --ai claude
```

### OpenAI Integration

```bash
export OPENAI_API_KEY=your-key
rulebird check --ai openai
```

### Local LLM (Ollama)

```bash
# Install Ollama first
rulebird check --ai local
```

## Commands Reference

### Core Commands

```bash
rulebird check [OPTIONS] [RULES]    # Check rules
rulebird init                       # Initialize config
rulebird explain RULE_ID            # Explain a specific rule
rulebird report                     # Generate compliance report
```

### Shortcuts

```bash
rulebird preflight    # Same as: check --phase preflight
rulebird postflight   # Same as: check --phase postflight
```

### Options

- `--phase`: Which phase to check (preflight, inflight, postflight, security, all)
- `--fix`: Attempt to auto-fix issues
- `--enforce`: Exit with error code if rules fail
- `--ai`: AI provider to use (claude, openai, cursor, local, none)
- `--json`: Output in JSON format
- `--quiet`: Minimal output
- `--verbose`: Detailed output

## Example Workflows

### For Human Developers

```bash
# Start your day
rulebird preflight

# Make changes to code...

# Before committing
rulebird postflight --fix

# Generate report for team
rulebird report --format markdown --output compliance.md
```

### For CI/CD

```yaml
# .github/workflows/rulebird.yml
name: RuleBird Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install RuleBird
        run: pip install rulebird
      - name: Run RuleBird
        run: rulebird check --enforce
```

### For AI Agents

```python
# In agent instructions
AGENT_RULES = """
1. Before starting any task, run: rulebird preflight
2. After implementing features, run: rulebird check --phase inflight
3. Before marking task complete, run: rulebird postflight --enforce
4. If any checks fail, fix them before proceeding
"""
```

## Audit Logging

RuleBird logs all checks to `.rulebird/audit.jsonl`:

```json
{"timestamp": "2025-01-20T10:30:00Z", "rule": "S1", "status": "failed", "message": "Hardcoded API key detected", "severity": "error"}
{"timestamp": "2025-01-20T10:30:01Z", "rule": "C1", "status": "passed", "message": "No warnings found", "severity": "error"}
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file.

## Links

- **GitHub**: [https://github.com/deftio/rulebird](https://github.com/deftio/rulebird)
- **Issues**: [https://github.com/deftio/rulebird/issues](https://github.com/deftio/rulebird/issues)
- **Rules Documentation**: [codebase-rules.md](../codebase-rules.md)

---

Made with ❤️ for developers and AI agents who care about code quality