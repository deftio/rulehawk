# CLI Command Reference

## Overview

RuleHawk provides a comprehensive command-line interface for rule checking, configuration, and integration.

## Global Options

These options work with all commands:

```bash
rulehawk [OPTIONS] COMMAND [ARGS]

Options:
  --help           Show help message
  --version        Show version
  --quiet          Minimal output
  --verbose        Detailed output
  --json           Output in JSON format
```

## Commands

### `init` - Initialize RuleHawk

Creates initial configuration in your project.

```bash
rulehawk init [OPTIONS]

Options:
  --with-scripts   Also generate integration scripts
  --force          Overwrite existing configuration

Examples:
  rulehawk init                  # Create rulehawk.yaml
  rulehawk init --with-scripts   # Also show integration options
  rulehawk init --force          # Overwrite existing config
```

**Creates**:
- `rulehawk.yaml` with default configuration

**Safety**: Won't overwrite existing files unless `--force` is used.

### `preflight` - Pre-work Checks

Run checks before starting development.

```bash
rulehawk preflight [OPTIONS]

Options:
  --fix            Auto-fix issues where possible
  --output FORMAT  Output format (yaml|json|markdown)

Examples:
  rulehawk preflight              # Run preflight checks
  rulehawk preflight --fix        # Auto-fix issues
  rulehawk preflight --output yaml  # YAML output for agents
```

**Checks**:
- Clean working directory
- Correct branch
- Dependencies up to date

### `inflight` - During Development Checks

Run checks while coding.

```bash
rulehawk inflight [OPTIONS]

Options:
  --fix            Auto-fix issues where possible
  --output FORMAT  Output format (yaml|json|markdown)

Examples:
  rulehawk inflight               # Run inflight checks
  rulehawk inflight --fix         # Auto-fix issues
```

**Checks**:
- New code has tests
- Documentation updated
- No debug code

### `postflight` - Pre-commit Checks

Run comprehensive checks before committing.

```bash
rulehawk postflight [OPTIONS]

Options:
  --fix            Auto-fix issues where possible
  --output FORMAT  Output format (yaml|json|markdown)

Examples:
  rulehawk postflight             # Run all pre-commit checks
  rulehawk postflight --fix       # Fix what can be fixed
```

**Checks**:
- All tests pass
- Code coverage met
- No warnings
- Security scan clean

### `check` - Run All Checks

Run checks for all phases or specific rules.

```bash
rulehawk check [OPTIONS] [RULES]

Options:
  --phase PHASE        Which phase to check (all|preflight|inflight|postflight|security)
  --fix                Auto-fix issues
  --output FORMAT      Output format (yaml|json|markdown)
  --verbosity LEVEL    Verbosity (minimal|normal|verbose)
  --show-skipped       Show skipped rules
  --ai PROVIDER        AI provider for complex checks (none|claude|openai)

Arguments:
  RULES                Specific rule IDs to check

Examples:
  rulehawk check                     # Check all rules
  rulehawk check --phase security    # Security rules only
  rulehawk check S1 S2              # Specific rules
  rulehawk check --fix              # Auto-fix issues
  rulehawk check --output yaml      # For AI agents
  rulehawk check --show-skipped     # Include skipped rules
```

### `integrate` - Generate Integration Scripts

Generate project-specific integration scripts.

```bash
rulehawk integrate [OPTIONS]

Options:
  --write          Actually write files (preview by default)
  --type TYPE      Force project type (auto|npm|python|make|shell)

Examples:
  rulehawk integrate              # Preview integration
  rulehawk integrate --write      # Create integration files
  rulehawk integrate --type npm   # Force npm integration
```

**Generates**:
- npm scripts for Node.js
- Makefile targets for Python/C++
- Cargo aliases for Rust
- Shell scripts for others

### `explain` - Explain a Rule

Get detailed information about a specific rule.

```bash
rulehawk explain RULE_ID

Arguments:
  RULE_ID          Rule identifier (e.g., S1, C2)

Examples:
  rulehawk explain S1     # Explain "No Hardcoded Secrets"
  rulehawk explain C2     # Explain "Test Coverage"
```

**Shows**:
- Rule description
- Phase and severity
- Whether auto-fixable
- Examples

### `mcp` - Start MCP Server

Start Model Context Protocol server for AI agents.

```bash
rulehawk mcp [OPTIONS]

Options:
  --port PORT           Server port (default: 5173)
  --host HOST           Server host (default: localhost)
  --interactive         Use interactive learning mode (default)
  --classic             Use classic mode without learning

Examples:
  rulehawk mcp                    # Interactive mode on localhost:5173
  rulehawk mcp --port 8080        # Custom port
  rulehawk mcp --classic          # Non-learning mode
  rulehawk mcp --host 0.0.0.0     # Listen on all interfaces
```

**Modes**:
- **Interactive**: RuleHawk learns commands from agents
- **Classic**: Static behavior, no learning

### `report` - Generate Compliance Report

Generate a detailed compliance report.

```bash
rulehawk report [OPTIONS]

Options:
  --format FORMAT   Output format (text|json|markdown)
  --output FILE     Save to file (default: stdout)

Examples:
  rulehawk report                        # Text report to console
  rulehawk report --format markdown      # Markdown format
  rulehawk report --output report.md     # Save to file
  rulehawk report --format json > ci.json  # JSON for CI
```

### `security` - Security Checks

Run security-focused rules.

```bash
rulehawk security [OPTIONS]

Options:
  --fix            Auto-fix issues where possible
  --output FORMAT  Output format (yaml|json|markdown)

Examples:
  rulehawk security              # Run security scan
  rulehawk security --fix        # Fix security issues
```

**Checks**:
- No hardcoded secrets
- Secure credential storage
- Input validation
- Dependency vulnerabilities

## Output Formats

### YAML (Default for agents)
```yaml
summary:
  total: 10
  passed: 8
  failed: 2
violations:
  - rule: S1
    message: "Hardcoded API key found"
```

### JSON
```json
{
  "summary": {
    "total": 10,
    "passed": 8,
    "failed": 2
  },
  "violations": [...]
}
```

### Markdown (Human-readable)
```markdown
## Summary
- Total: 10 rules
- Passed: 8
- Failed: 2

## Violations
- **S1**: Hardcoded API key found
```

## Verbosity Levels

### Minimal
```
2 violations found
```

### Normal (Default)
```
S1: No Hardcoded Secrets - FAILED
  Found API key in config.py:42
C2: Test Coverage - FAILED
  Coverage 75% below threshold 80%
```

### Verbose
```
S1: No Hardcoded Secrets - FAILED
  File: config.py
  Line: 42
  Pattern: api_key = "sk-..."
  Suggestion: Use environment variable
  Fix: Move to .env file
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | One or more rules failed |
| 2 | Configuration error |
| 3 | Tool not found |
| 127 | Command not found |

## Environment Variables

```bash
# Set config file
export RULEHAWK_CONFIG=custom.yaml

# Set log level
export RULEHAWK_LOG_LEVEL=DEBUG

# Disable colors
export NO_COLOR=1

# Set AI provider
export RULEHAWK_AI_PROVIDER=claude
```

## Configuration Override

Override configuration from command line:

```bash
# Override config file
rulehawk check --config custom.yaml

# Override specific rules
rulehawk check --set rules.C2.threshold=75

# Disable specific phases
rulehawk check --skip-phase security
```

## Shell Completion

Enable tab completion for your shell:

### Bash
```bash
eval "$(_RULEHAWK_COMPLETE=bash_source rulehawk)"
```

### Zsh
```zsh
eval "$(_RULEHAWK_COMPLETE=zsh_source rulehawk)"
```

### Fish
```fish
_RULEHAWK_COMPLETE=fish_source rulehawk | source
```

## Aliases

Useful shell aliases:

```bash
# Quick checks
alias rhp="rulehawk preflight"
alias rhi="rulehawk inflight"
alias rhpost="rulehawk postflight"

# Fix issues
alias rhfix="rulehawk check --fix"

# CI mode
alias rhci="rulehawk check --output json --verbosity minimal"
```

## Common Workflows

### Development Workflow
```bash
# Start work
rulehawk preflight

# During coding
rulehawk inflight

# Before commit
rulehawk postflight --fix
git commit
```

### CI/CD Pipeline
```bash
# In CI script
rulehawk check --output json > results.json
if [ $? -ne 0 ]; then
  echo "RuleHawk checks failed"
  exit 1
fi
```

### AI Agent Workflow
```bash
# Start MCP server
rulehawk mcp --interactive &

# Agent connects and uses MCP API
# ...

# Or direct CLI
rulehawk check --output yaml
```

## Debugging

### Debug Mode
```bash
RULEHAWK_LOG_LEVEL=DEBUG rulehawk check
```

### Dry Run
```bash
rulehawk check --dry-run
```

### Test Specific Rule
```bash
rulehawk check S1 --verbose
```

### Show Configuration
```bash
rulehawk show-config
```

## Examples

### Fix All Auto-fixable Issues
```bash
rulehawk check --fix
```

### Check Only Changed Files
```bash
# Coming soon
rulehawk check --changed-only
```

### Generate and Apply Integration
```bash
rulehawk integrate --write
```

### Full Pre-commit Check
```bash
rulehawk postflight --fix --output yaml
```

## Next Steps

- [Configuration Guide](configuration.md) - Customize RuleHawk
- [Integration Guide](integration.md) - Connect with your tools
- [MCP Integration](mcp.md) - For AI agents
- [Troubleshooting](troubleshooting.md) - Common issues