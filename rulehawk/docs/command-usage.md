# RuleHawk Command Usage

This guide clarifies how to use RuleHawk commands. The key insight is that checking is the default behavior - you only add flags when you want different behavior.

## The Simple Command Structure

RuleHawk commands follow a consistent pattern where checking is implicit:

```bash
rulehawk <phase>           # Check rules (default behavior)
rulehawk <phase> --fix     # Fix issues
rulehawk <phase> --output json  # Check with different output format
```

## No --check Flag Needed

There is no `--check` flag because checking is the default behavior:

```bash
# These all CHECK rules (no flag needed):
rulehawk preflight         # Checks preflight rules
rulehawk postflight        # Checks postflight rules
rulehawk security          # Checks security rules
rulehawk check             # Checks all rules

# Add --fix only when you want to modify files:
rulehawk preflight --fix   # Fixes preflight issues
rulehawk postflight --fix  # Fixes postflight issues
```

## When to Use Which Command

The table below shows common scenarios and the exact command to use:

| What You Want | Command to Use | What Happens |
|--------------|----------------|--------------|
| **See current violations** | `rulehawk postflight` | Shows violations, exits 1 if any found |
| **Fix formatting issues** | `rulehawk postflight --fix` | Modifies files, fixes what it can |
| **CI/CD pipeline check** | `rulehawk postflight` | Fails build if violations (exit 1) |
| **Get JSON for parsing** | `rulehawk postflight --output json` | Returns JSON, exits 1 if violations |
| **Check everything** | `rulehawk check` | Checks all rules across all phases |
| **Human-readable report** | `rulehawk postflight --output markdown` | Pretty output for humans |

## Default Output Format (YAML)

When you run RuleHawk without specifying output format, it returns YAML by default:

```bash
$ rulehawk postflight
```

Returns structured YAML output:
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
```

## For Different Users

Each type of user has specific patterns that work best:

### Developers

During development, you'll typically check and fix iteratively:

```bash
# See what needs attention
rulehawk postflight --output markdown

# Fix what can be automated
rulehawk postflight --fix

# Check again to see what needs manual work
rulehawk postflight --output markdown
```

### CI/CD Systems

In pipelines, use the default check behavior which provides proper exit codes:

```yaml
# GitHub Actions - this fails the build if issues exist
- name: Validate Code Quality
  run: rulehawk postflight
```

### AI Agents

Agents should use YAML output to create tasks without consuming context:

```
Instructions for agent:
1. Run: rulehawk preflight
   Parse the YAML output to see initial state

2. During work, run: rulehawk inflight --fix
   This fixes issues as you go

3. Before completing, run: rulehawk postflight --fix
   Then run: rulehawk postflight
   If exit code is 1, parse YAML to see remaining issues
```

## Exit Codes Explained

Understanding exit codes helps you use RuleHawk correctly in scripts:

- **Exit 0** - No violations found (check mode) OR all issues fixed (fix mode)
- **Exit 1** - Violations found (check mode) OR unfixable issues remain (fix mode)
- **Exit 2** - Configuration error or tool failure

This means CI/CD naturally works:
```bash
# This command fails the build if any violations exist
rulehawk postflight || exit 1
```

## Common Mistakes to Avoid

These are incorrect usage patterns to avoid:

```bash
# WRONG - there is no --check flag
rulehawk postflight --check

# WRONG - don't combine output formats
rulehawk postflight --output yaml --output json

# WRONG - fix doesn't take arguments
rulehawk postflight --fix A1

# CORRECT versions:
rulehawk postflight           # Check rules
rulehawk postflight --output json  # Check with JSON output
rulehawk postflight --fix     # Fix all fixable issues
```

## Summary

The key points to remember:

- **No --check flag exists** - checking is the default behavior
- **Add --fix only to modify files** - otherwise you're checking
- **YAML is default output** - use --output for other formats
- **Exit codes work for CI/CD** - no special flags needed
- **Commands are simple** - phase name, optional --fix or --output

This design keeps commands short and predictable while providing all needed functionality.