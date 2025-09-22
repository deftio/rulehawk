# RuleHawk 🦅

RuleHawk is a lightweight CLI tool that enforces codebase rules for both human developers and AI agents. It provides external validation that rules are actually followed, not just documented.

```
    ___
   (o,o)    RuleHawk v0.1.0
  <  .  >   Keeping your code in check
   -=--
```

## The Problem RuleHawk Solves

When working with AI coding agents or multiple developers, maintaining consistent code quality becomes challenging:

- **AI agents** lose track of rules as context grows, claim false compliance, or selectively follow guidelines
- **Human developers** forget to run formatters, skip tests when rushing, or debate style in reviews
- **Documentation** like `agent.md` or `CONTRIBUTING.md` provides guidelines but no enforcement
- **Production** breaks from preventable issues that automated checks could have caught

RuleHawk solves this by making rules checkable and enforceable, not just documented.

## Rules vs Tasks

Understanding this distinction is critical for using RuleHawk effectively:

- **Rules** are persistent quality standards (how you build): "No hardcoded secrets", "100% test coverage"
- **Tasks** are specific work items (what you build): "Add user authentication", "Fix bug #123"

RuleHawk enforces rules, not tasks. It ensures quality standards are met regardless of what feature you're building.

## Quick Start

### Installation

Install RuleHawk in your development environment:

```bash
# From PyPI (coming soon)
pip install rulehawk

# From source
git clone https://github.com/deftio/rulehawk.git
cd rulehawk
pip install -e .
```

### Initialize Your Project

Create a `rulehawk.yaml` configuration file in your project:

```bash
cd your-project
rulehawk init
```

This generates a comprehensive `rulehawk.yaml` with default rules you can customize.

### Basic Usage

RuleHawk uses a simple two-mode design where checking is the default behavior:

```bash
# Check rules (default - returns YAML, exits 1 if violations)
rulehawk preflight         # Check preflight rules
rulehawk postflight        # Check postflight rules
rulehawk check             # Check all rules

# Fix mode (modifies files to fix issues)
rulehawk preflight --fix   # Fix preflight issues
rulehawk postflight --fix  # Fix postflight issues

# Different output formats
rulehawk postflight --output json      # JSON for parsing
rulehawk postflight --output markdown  # Human-readable
```

## For AI Agents

RuleHawk is designed to be simple for AI agents to use. Instead of remembering complex rules, agents just run commands:

### Agent Workflow

Include this in your agent instructions for seamless integration:

```
Before starting any coding task, run: rulehawk preflight
Parse the YAML output to understand initial state.

After making changes, run: rulehawk inflight --fix
This automatically fixes formatting and simple issues.

Before marking task complete, run: rulehawk postflight --fix
Then run: rulehawk postflight
If exit code is 1, parse the YAML output to see remaining issues and fix them.
```

### Why Agents Need RuleHawk

AI agents often exhibit these problematic behaviors:

- **False confidence** - Claiming "all tests pass" when they don't
- **Context drift** - Forgetting rules mentioned earlier
- **Selective compliance** - Following some rules while ignoring others

RuleHawk provides external validation that agents cannot override or misinterpret.

## For Human Developers

RuleHawk integrates naturally into your development workflow:

### IDE Integration

Configure your editor to run RuleHawk on save:

```json
// VS Code settings.json
{
  "runOnSave.commands": [
    {
      "match": "\\.(py|js|ts)$",
      "command": "rulehawk check --fix",
      "runIn": "backend"
    }
  ]
}
```

### Git Hooks

Add automatic checking before commits:

```bash
# .git/hooks/pre-commit
#!/bin/bash
rulehawk postflight || exit 1
```

### CI/CD Integration

Enforce rules in your pipeline:

```yaml
# GitHub Actions
- name: Check Codebase Rules
  run: |
    pip install rulehawk
    rulehawk check --enforce
```

## Understanding rulehawk.yaml

The `rulehawk.yaml` file defines all rules and configuration. Here's what each section does:

### Configuration Section

Controls how RuleHawk operates:

```yaml
config:
  ai_provider: none       # AI for complex checks (claude|openai|none)
  enabled_phases:         # Which phases to run by default
    - preflight
    - postflight
    - security
  ignore_paths:           # Paths to skip
    - node_modules/
    - .venv/
```

### Rules Section

Defines quality standards with these key fields:

```yaml
rules:
  S1:
    name: No Hardcoded Secrets
    phase: security       # When it runs (always|preflight|postflight|security)
    severity: error       # Impact (error|warning|info)
    description: |        # What and why
      Never commit credentials in code
    check:               # How to validate
      command: "gitleaks detect"
    auto_fixable: false  # Can RuleHawk fix it automatically
```

### Custom Rules Section

Add project-specific rules:

```yaml
custom_rules:
  CUSTOM-01:
    name: Your Custom Rule
    phase: postflight
    severity: warning
    check:
      command: "your-check-command"
```

## Available Rules

RuleHawk includes comprehensive rules organized by phase:

### Security Rules (S1-S8)

These rules protect against security vulnerabilities:

- **S1: No Hardcoded Secrets** - Prevent credential leaks
- **S2: Secure Storage** - Use proper secret management
- **S3: Auth Best Practices** - Standard authentication patterns
- **S4: Input Validation** - Prevent injection attacks
- **S5: Dependency Security** - Scan for vulnerabilities

### Quality Rules (C1-C5)

These rules ensure code quality and maintainability:

- **C1: Zero Warnings** - Clean builds without warnings
- **C2: Test Coverage** - Minimum 80% coverage
- **C3: CI Must Pass** - All automated checks green
- **C4: Documentation** - Complete API docs
- **C5: Security Review** - Verify security compliance

### Practice Rules (A1-A3, P1-P2, F1-F3)

These rules enforce development best practices:

- **A1: Code Formatting** - Consistent style
- **A2: Organize Files** - Proper project structure
- **A3: Branch Protection** - No direct commits to main
- **P1: Environment Check** - Verify setup before starting
- **F1: Document APIs** - Public interfaces documented

## When to Use Each Mode

Understanding when to use check vs fix mode ensures you get the desired behavior:

| Your Situation | Use This Command | What It Does |
|---------------|-----------------|--------------|
| **See current violations** | `rulehawk postflight` | Shows issues in YAML, exits 1 if any found |
| **CI/CD pipeline** | `rulehawk postflight` | Fails build (exit 1) if violations exist |
| **Fix formatting issues** | `rulehawk postflight --fix` | Modifies files, fixes what it can |
| **Get JSON for parsing** | `rulehawk postflight --output json` | Returns JSON, exits 1 if violations |
| **Human-readable report** | `rulehawk postflight --output markdown` | Pretty output for developers |
| **Agent parsing** | `rulehawk check` | Returns YAML for task creation |

The key insight is that checking is the default behavior - you only add `--fix` when you want to modify files.

## Commands Reference

RuleHawk provides these commands for different use cases:

### Core Commands

These are the primary commands you'll use:

- **`rulehawk check [OPTIONS] [RULES]`** - Check specified rules or all rules
- **`rulehawk init`** - Create rulehawk.yaml in current directory
- **`rulehawk explain RULE_ID`** - Show detailed information about a rule
- **`rulehawk report`** - Generate compliance report

### Convenience Shortcuts

These shortcuts make common workflows easier:

- **`rulehawk preflight`** - Alias for `check --phase preflight`
- **`rulehawk postflight`** - Alias for `check --phase postflight`

### Command Options

Modify command behavior with these options:

- **`--phase`** - Check specific phase (preflight|inflight|postflight|security|all)
- **`--fix`** - Automatically fix violations where possible
- **`--enforce`** - Exit with code 1 if any rules fail
- **`--ai`** - Use AI provider for complex checks (claude|openai|cursor|local)
- **`--json`** - Output results in JSON format
- **`--quiet`** - Suppress non-error output
- **`--verbose`** - Show detailed information

## JSON Output for Automation

Get machine-readable output for integration with other tools:

```bash
rulehawk check --json
```

Output format:
```json
{
  "timestamp": "2025-01-20T10:30:00Z",
  "total_count": 15,
  "passed_count": 13,
  "failed_count": 2,
  "details": [
    {
      "rule_id": "S1",
      "name": "No Hardcoded Secrets",
      "status": "failed",
      "message": "Found hardcoded API key",
      "files": ["config.py:45"]
    }
  ]
}
```

## Extending RuleHawk

Customize RuleHawk for your specific needs:

### Adding Custom Rules

Edit the `custom_rules` section in your `rulehawk.yaml`:

```yaml
custom_rules:
  ORG-01:
    name: Organization Specific Check
    phase: postflight
    severity: error
    description: |
      Enforce organization-specific standards
    check:
      command: "your-validation-script"
```

### AI Provider Integration

Configure AI for semantic rule checking:

```yaml
config:
  ai_provider: claude  # or openai, cursor, local

rules:
  DOC-01:
    check:
      ai: "Verify all functions have meaningful names"
```

### Custom Validators

For complex logic, write Python validators:

```python
# validators.py
def check_custom_rule(config):
    # Your validation logic
    return {
        'success': True,
        'message': 'Check passed'
    }
```

## Troubleshooting

Common issues and their solutions:

### Missing Tools

If RuleHawk reports a tool is missing:

- **Python**: Install with `pip install ruff pytest`
- **JavaScript**: Install with `npm install -D eslint prettier`
- **Security**: Install with `pip install gitleaks bandit`

### AI Provider Not Working

Check your configuration and environment:

1. Verify `ai_provider` is set in rulehawk.yaml
2. Ensure API keys are set (e.g., `OPENAI_API_KEY`)
3. Test with `rulehawk check S1 --ai claude --verbose`

### Rules Not Running

Verify rule configuration:

1. Check rule phase matches your command
2. Ensure rule isn't disabled in config
3. Run with `--verbose` for detailed output

## Contributing

We welcome contributions to RuleHawk:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Resources

Additional documentation and resources:

- **[Introduction to Rules](docs/introduction.md)** - Why rules matter and how they work
- **[Architecture Guide](docs/architecture.md)** - Technical design and internals
- **[Custom Rules Guide](docs/custom-rules.md)** - Creating project-specific rules
- **[Codebase Rules](../docs/codebase-rules.md)** - Full rule documentation

## Support

Get help and report issues:

- **GitHub Issues**: [github.com/deftio/rulehawk/issues](https://github.com/deftio/rulehawk/issues)
- **Discussions**: [github.com/deftio/rulehawk/discussions](https://github.com/deftio/rulehawk/discussions)

Remember: RuleHawk is about automating quality checks so you can focus on building great software.