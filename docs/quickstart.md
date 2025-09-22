# Quick Start Guide

Get RuleHawk running in your project in 5 minutes.

## 1. Install RuleHawk in Your Project

### Option A: Install from PyPI (when published)
```bash
# In your project directory
cd ~/my-project

# Install RuleHawk like any other library
pip install rulehawk
# or
uv add rulehawk
```

### Option B: Install from GitHub (current method)
```bash
# In your project directory
cd ~/my-project

# Install directly from GitHub
pip install git+https://github.com/deftio/rulehawk.git
# or with uv
uv pip install git+https://github.com/deftio/rulehawk.git
```

## 2. Initialize RuleHawk

```bash
# You're already in your project directory
# Initialize RuleHawk configuration
rulehawk init
```

This creates `rulehawk.yaml` with sensible defaults.

## 3. Run Your First Check

```bash
rulehawk preflight
```

You'll see output like:
```yaml
summary:
  total: 5
  passed: 3
  failed: 0
  skipped: 2
```

## 4. Integrate with Your Project

Generate project-specific commands:

```bash
uv run rulehawk integrate
```

This shows you how to add RuleHawk to your existing workflow:
- **Node.js**: Adds npm scripts to package.json
- **Python**: Shows commands for your setup
- **Make**: Provides Makefile targets

## 5. Use Native Commands

After integration, use familiar commands:

```bash
# Node.js projects
npm run preflight   # Before starting work
npm run postflight  # Before committing

# Python/Make projects
make preflight      # Before starting work
make postflight     # Before committing
```

## For AI Agents

### Quick Setup

```bash
# Start interactive MCP server
rulehawk mcp --interactive

# RuleHawk will learn your project's commands
```

### Direct CLI Usage

```bash
# Get structured output for parsing
rulehawk check --output yaml
```

## Common Tasks

### Skip Rules That Don't Apply

Create `rulehawkignore`:
```
A3:We use trunk-based development
P2:Task planning not needed for hotfixes
```

### Auto-fix Issues

```bash
rulehawk check --fix
```

### Check Specific Phase

```bash
rulehawk preflight   # Before work
rulehawk inflight    # During coding
rulehawk postflight  # Before commit
```

### Get Help on a Rule

```bash
rulehawk explain S1
```

## Example Output

### Success
```yaml
summary:
  total: 10
  passed: 10
  failed: 0
```

### With Issues
```yaml
summary:
  total: 10
  passed: 8
  failed: 2
violations:
  - rule: A1
    name: Code Formatting
    message: "Would reformat: src/app.py"
    fixable: true
  - rule: C2
    name: Test Coverage
    message: "Coverage 75% below threshold 80%"
```

## Workflow Example

```bash
# Morning: Start new feature
$ rulehawk preflight
✅ All preflight checks passed

# During development
$ rulehawk inflight
⚠️ 1 warning: Missing tests for new function

# Before committing
$ rulehawk postflight --fix
🔧 Fixed code formatting
✅ All postflight checks passed

# Commit with confidence
$ git commit -m "Add new feature"
```

## Next Steps

- **[Configure rules](configuration.md)** for your project
- **Set up exceptions** in rulehawkignore for rules that don't apply
- **Integrate with CI/CD** for automated checking
- **[Use MCP](mcp.md)** for AI agent integration

## Get Help

```bash
# See all commands
rulehawk --help

# Get help on specific command
rulehawk check --help

# Explain a rule
rulehawk explain C2
```

## Tips

1. **Start simple** - Use default configuration first
2. **Add incrementally** - Enable rules gradually
3. **Document exceptions** - Explain why rules are skipped
4. **Commit everything** - Share learned commands via git
5. **Use native commands** - Integrate with npm/make/cargo

## Troubleshooting

### RuleHawk not found?
```bash
# Ensure virtual environment is active
source venv/bin/activate  # or: uv venv
```

### Config already exists?
```bash
# RuleHawk won't overwrite without permission
rulehawk init --force  # Only if you want to reset
```

### Need different output?
```bash
# For humans
rulehawk check

# For agents
rulehawk check --output yaml

# For CI
rulehawk check --output json
```

Ready to improve your code quality? Start with `rulehawk init`!