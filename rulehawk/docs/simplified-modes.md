# RuleHawk Simplified Mode Design

This document describes the simplified two-mode design for RuleHawk that provides everything needed without unnecessary complexity.

## The Two Modes

RuleHawk operates in just two modes that cover all use cases:

### Check Mode (Default)

Returns a structured list of rule violations and exits with appropriate code:

```bash
rulehawk preflight          # Check preflight rules
rulehawk postflight         # Check postflight rules
rulehawk check              # Check all rules
```

**Behavior:**
- **Returns** structured output (YAML by default, JSON or Markdown available)
- **Exit code 0** if no violations found
- **Exit code 1** if violations found
- **Never modifies** any files
- **Perfect for** CI/CD, agents parsing output, developers exploring

**Output format (YAML default):**
```yaml
summary:
  total: 15
  passed: 13
  failed: 2

violations:
  - rule: S1
    name: No Hardcoded Secrets
    severity: error
    file: config.py
    line: 45
    message: API key found in code
    fixable: false

  - rule: A1
    name: Code Formatting
    severity: warning
    files:
      - src/main.py
      - src/utils.py
    message: 2 files need formatting
    fixable: true
    fix_command: ruff format
```

### Fix Mode

Attempts to automatically fix violations where possible:

```bash
rulehawk preflight --fix    # Fix preflight issues
rulehawk postflight --fix   # Fix postflight issues
rulehawk check --fix        # Fix all issues
```

**Behavior:**
- **Modifies files** to fix issues (formatting, imports, etc.)
- **Returns** structured output showing what was fixed and what remains
- **Exit code 0** if all issues fixed or no issues found
- **Exit code 1** if unfixable issues remain
- **Perfect for** development workflow, pre-commit hooks

**Output format (YAML):**
```yaml
summary:
  total_issues: 5
  fixed: 3
  remaining: 2

fixed:
  - rule: A1
    name: Code Formatting
    files_modified: 12

  - rule: C1
    name: Import Sorting
    files_modified: 3

remaining:
  - rule: S1
    name: No Hardcoded Secrets
    severity: error
    file: config.py
    line: 45
    message: Cannot auto-fix - manual intervention required
    instructions: Move API key to environment variable
```

## Output Formats

Choose the output format that works best for your use case:

### YAML (Default)

Best for agents and programmatic parsing:

```bash
rulehawk check                    # YAML output
rulehawk check --output yaml      # Explicit YAML
```

**Why YAML default:**
- **Structured** for easy parsing by agents/tools
- **Human-readable** without special rendering
- **Convertible** to tasks/todos programmatically
- **Compact** compared to JSON

### JSON

For tools that prefer JSON:

```bash
rulehawk check --output json
```

### Markdown

For human consumption and reports:

```bash
rulehawk check --output markdown
```

## Usage Patterns

Different scenarios and how to handle them:

### CI/CD Pipeline

Simply use check mode - it provides the exit code needed:

```yaml
# GitHub Actions
- name: Check Code Quality
  run: rulehawk postflight --check
  # Fails build if violations found (exit code 1)

# Or with attempted fixes first
- name: Fix Issues
  run: rulehawk postflight --fix
  continue-on-error: true

- name: Verify Clean
  run: rulehawk postflight --check
```

### Agent Workflow

Agents can parse the structured output to create tasks:

```python
# Agent pseudocode
result = run_command("rulehawk postflight --check --output yaml")
data = yaml.parse(result.stdout)

if data['summary']['failed'] > 0:
    # Convert violations to tasks
    tasks = []
    for violation in data['violations']:
        if violation['fixable']:
            tasks.append(f"Run: rulehawk --fix {violation['rule']}")
        else:
            tasks.append(f"Manual fix: {violation['message']}")

    # Work through tasks without consuming context window
    for task in tasks:
        execute_task(task)
```

### Developer Workflow

Developers get immediate feedback with actionable information:

```bash
# Check current state
$ rulehawk check
# See YAML output with violations

# Fix what's possible
$ rulehawk check --fix
# See what was fixed and what remains

# Check specific phase
$ rulehawk preflight --check
```

## Why This Design Works

This simplified approach provides everything needed:

1. **CI/CD compatibility** - Exit codes work with any build system
2. **Agent-friendly** - Structured output can be parsed, not ingested
3. **Developer-friendly** - Clear feedback and auto-fix capability
4. **No mode confusion** - Just check or fix, nothing else
5. **Predictable behavior** - Check reports, fix modifies

## Migration from Three-Mode Design

If you were using the three-mode design (check/fix/enforce):

- Replace `--enforce` with `--check` (it returns exit code 1 on violations)
- Keep `--fix` as is
- Remove the `--check` flag (it's the default)

Old:
```bash
rulehawk postflight --enforce  # Strict validation
```

New:
```bash
rulehawk postflight --check    # Same effect - fails on violations
# or just
rulehawk postflight            # --check is default
```

## Environment Variables

Control behavior through environment variables:

```bash
# Set default output format
export RULEHAWK_OUTPUT=json

# Set verbosity
export RULEHAWK_VERBOSE=true

# Set specific config file
export RULEHAWK_CONFIG=./custom-rules.yaml
```

## Exit Codes

Standard exit codes for scripting:

- **0** - Success (no violations in check mode, all fixed in fix mode)
- **1** - Violations found (check mode) or unfixable issues (fix mode)
- **2** - Error (missing config, invalid rule, etc.)
- **127** - Command not found (rulehawk not installed)

## Examples

Real-world usage examples:

### Make Integration

```makefile
.PHONY: check fix test

check:
	@rulehawk postflight --output markdown

fix:
	@rulehawk postflight --fix

test: check
	pytest

ci: fix
	rulehawk postflight --check  # Fails if issues remain
```

### NPM Scripts

```json
{
  "scripts": {
    "lint": "rulehawk check --output json",
    "lint:fix": "rulehawk check --fix",
    "pretest": "npm run lint",
    "test": "jest"
  }
}
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Try to fix issues
rulehawk postflight --fix

# Verify everything is clean
rulehawk postflight --check || {
  echo "❌ RuleHawk found issues. Please fix before committing."
  exit 1
}
```

## Summary

The two-mode design is simpler and more powerful:

- **Check mode** provides structured output and proper exit codes for CI/CD
- **Fix mode** handles automatic fixes with clear reporting
- **YAML default output** enables agents to parse without context consumption
- **No enforce mode needed** - check mode handles that use case

This design follows the Unix philosophy: do one thing well, use exit codes properly, and output structured data that other tools can consume.