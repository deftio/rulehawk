# RuleHawk Command Structure

This document explains RuleHawk's command structure, modes of operation, and how it integrates with build tools and CI/CD pipelines.

## Command Consistency

All RuleHawk commands follow a consistent pattern for predictable behavior:

```bash
rulehawk <phase> [--check|--fix|--enforce]
```

The phases determine which rules to run:
- **preflight** - Rules to check before starting work (environment, setup)
- **inflight** - Rules to check during development (documentation, tests)
- **postflight** - Rules to check before committing (warnings, coverage)
- **security** - Security-specific rules
- **all** - Run all rules (default)

## Operation Modes

Each command can run in one of three modes that control behavior:

### Check Mode (Default)

The default mode reports issues without making changes or failing builds:

```bash
rulehawk preflight          # Check preflight rules, report issues
rulehawk preflight --check  # Explicit check mode (same as above)
rulehawk postflight         # Check postflight rules
```

**Behavior:**
- **Reports** all rule violations
- **Returns** exit code 0 (success) regardless of violations
- **Safe** for exploration and debugging
- **Never** modifies code

**Use when:**
- Exploring current compliance status
- Running in development environment
- Wanting informational feedback

### Fix Mode

Attempts to automatically fix violations where possible:

```bash
rulehawk preflight --fix
rulehawk inflight --fix
rulehawk postflight --fix
```

**Behavior:**
- **Fixes** auto-fixable violations (formatting, simple issues)
- **Reports** unfixable violations
- **Returns** exit code 0 if all issues fixed, 1 if unfixable issues remain
- **Modifies** code files in place

**Use when:**
- During active development
- Before committing code
- In pre-commit hooks (with caution)

**What gets auto-fixed:**
- **Code formatting** (A1) - Runs formatters like ruff, prettier
- **Import sorting** - Organizes import statements
- **Trailing whitespace** - Removes unnecessary spaces
- **Simple linting issues** - Fixes basic style violations

**What CANNOT be auto-fixed:**
- **Security issues** (S1-S8) - Require human judgment
- **Logic errors** - Need understanding of intent
- **Missing tests** - Require writing new code
- **Documentation** - Needs human-written content

### Enforce Mode

Strict mode that exits with error code if any violations found:

```bash
rulehawk preflight --enforce
rulehawk postflight --enforce
```

**Behavior:**
- **Reports** all violations
- **Returns** exit code 1 if ANY violations found
- **Blocks** further execution in scripts/CI
- **Never** modifies code (use --fix separately first)

**Use when:**
- In CI/CD pipelines
- As gate before merging
- When compliance is mandatory

## Important: What Enforce Does NOT Do

Understanding what enforce mode doesn't do is critical to avoid confusion:

**Enforce does NOT:**
- **Fix issues automatically** - It only reports and fails
- **Call agents again** - It doesn't trigger any external processes
- **Modify your codebase** - It's read-only
- **Block git operations** - Unless you add it to hooks

**Enforce DOES:**
- **Exit with code 1** - This stops scripts/pipelines
- **Report violations** - Shows what needs fixing
- **Provide clear feedback** - Explains what failed and why

## Integration with Build Tools

RuleHawk is designed to integrate cleanly with existing build workflows:

### With Make

```makefile
.PHONY: check fix test build

check:
	rulehawk postflight --check

fix:
	rulehawk postflight --fix

test: fix
	pytest

build: test
	rulehawk postflight --enforce
	docker build -t myapp .
```

### With npm Scripts

```json
{
  "scripts": {
    "check": "rulehawk postflight --check",
    "fix": "rulehawk postflight --fix",
    "pretest": "npm run fix",
    "test": "jest",
    "prebuild": "rulehawk postflight --enforce",
    "build": "webpack"
  }
}
```

### With GitHub Actions

```yaml
jobs:
  quality:
    steps:
      - name: Check Rules (Informational)
        run: rulehawk postflight --check
        continue-on-error: true  # Don't fail build

      - name: Auto-fix Issues
        run: rulehawk postflight --fix

      - name: Enforce Rules (Gate)
        run: rulehawk postflight --enforce  # Will fail build if violations
```

## Workflow Examples

Different workflows for different scenarios:

### Development Workflow

During active development, use check and fix modes:

```bash
# Start work
rulehawk preflight --check     # See what needs attention

# During development
rulehawk inflight --fix        # Fix as you go

# Before commit
rulehawk postflight --fix      # Fix what can be fixed
rulehawk postflight --check    # See what remains
```

### CI/CD Workflow

In pipelines, enforce after attempting fixes:

```bash
# Try to fix simple issues
rulehawk all --fix

# Enforce all rules (fail if any violations)
rulehawk all --enforce
```

### Agent Workflow

For AI agents, be explicit about expectations:

```
Instructions for AI agent:
1. Run: rulehawk preflight --check
2. If issues found, address them
3. During work, periodically run: rulehawk inflight --fix
4. Before completing, run: rulehawk postflight --fix
5. Finally run: rulehawk postflight --enforce
6. If enforce fails, fix issues and repeat step 5
```

## Exit Codes

RuleHawk uses standard exit codes for scripting:

- **0** - Success (no violations OR all fixed OR check mode)
- **1** - Failure (violations found in enforce mode OR unfixable issues in fix mode)
- **2** - Error (configuration problem, missing tools, etc.)

## Safety Considerations

To use RuleHawk safely in production workflows:

### DO:
- **Test rules** in development before enforcing in CI
- **Use --check** first to understand current state
- **Run --fix** before --enforce** to avoid unnecessary failures
- **Configure ignore patterns** for generated files
- **Version control** your rulehawk.yaml

### DON'T:
- **Use --enforce** in development without understanding implications
- **Auto-fix in production** without review
- **Ignore persistent violations** - fix or adjust rules
- **Mix modes** in single command (pick one: check, fix, or enforce)

## Phase Selection

Choose the right phase for your context:

- **preflight** - Use when starting new work session
- **inflight** - Use periodically during development
- **postflight** - Use before commits/PRs
- **security** - Use for security audits
- **all** - Use in CI/CD for comprehensive checks

## Command Aliases

For convenience, these shortcuts map to full commands:

```bash
# These are equivalent:
rulehawk preflight              # Same as: rulehawk check --phase preflight
rulehawk postflight             # Same as: rulehawk check --phase postflight

# With modes:
rulehawk preflight --fix        # Same as: rulehawk check --phase preflight --fix
rulehawk postflight --enforce   # Same as: rulehawk check --phase postflight --enforce
```

## Summary

The consistent command structure ensures predictable behavior:

- **Default is safe** - Check mode never modifies or fails builds
- **Fix is helpful** - Automatically resolves simple issues
- **Enforce is strict** - Fails builds to maintain quality gates
- **Phases are contextual** - Run appropriate rules for your stage

This design allows RuleHawk to integrate smoothly with any workflow while maintaining clear boundaries about what it will and won't do.