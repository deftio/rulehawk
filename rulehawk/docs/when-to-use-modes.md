# When to Use Each RuleHawk Mode

This guide helps you choose the right mode (check, fix, or enforce) for your specific situation. Understanding when to use each mode ensures you get the behavior you want without unexpected surprises.

## Quick Decision Guide

The table below shows which mode to use based on your context and goals:

| Context | Goal | Mode to Use | Why |
|---------|------|------------|-----|
| **Development (exploring)** | See what rules exist | `--check` | Safe exploration, won't change anything |
| **Development (active coding)** | Clean up code while working | `--fix` | Automatically fixes formatting, simple issues |
| **Before committing** | Ensure code is clean | `--fix` then `--check` | Fix what's possible, see what needs manual attention |
| **CI/CD pipeline** | Gate before merge | `--enforce` | Fails build if any violations, prevents bad code merging |
| **Git pre-commit hook** | Prevent bad commits | `--fix` or `--enforce` | Fix for convenience, enforce for strictness |
| **Agent instruction** | During development | `--fix` | Let agent auto-fix as it works |
| **Agent instruction** | Final validation | `--enforce` | Ensure agent actually fixed everything |
| **Code review** | Verify compliance | `--check` | See issues without failing review builds |
| **Production deploy** | Final gate | `--enforce` | Absolute requirement before deploy |

## Detailed Mode Explanations

Each mode serves a specific purpose in the development lifecycle:

### Check Mode: Information Without Consequences

Use `--check` when you want to understand the current state without any side effects:

```bash
rulehawk postflight --check  # or just: rulehawk postflight
```

**When to use:**
- **First time** running RuleHawk in a project
- **Debugging** why a rule is failing
- **Learning** what rules apply to your code
- **Monitoring** compliance without blocking work

**What happens:**
- **Reports** all violations found
- **Never** modifies any files
- **Always** exits with code 0 (success)
- **Safe** to run anytime, anywhere

**Real example:**
```bash
# Developer exploring a new codebase
$ rulehawk postflight --check
🦅 RuleHawk checking postflight rules...
❌ C1: Zero Warnings - 5 linting warnings found
❌ S1: No Hardcoded Secrets - API key in config.py:45
✅ C2: Test Coverage - 85% coverage meets threshold
# Exit code: 0 (doesn't fail anything)
```

### Fix Mode: Automated Cleanup

Use `--fix` when you want RuleHawk to automatically resolve issues it can handle:

```bash
rulehawk postflight --fix
```

**When to use:**
- **During development** to maintain clean code as you work
- **Before committing** to auto-fix formatting and simple issues
- **In pre-commit hooks** for developer convenience
- **Agent workflows** to reduce manual fixes

**What happens:**
- **Modifies files** to fix issues (formatting, imports, etc.)
- **Reports** remaining unfixed issues
- **Exits 0** if all issues fixed
- **Exits 1** if unfixable issues remain

**Real example:**
```bash
# Developer cleaning up before commit
$ rulehawk postflight --fix
🦅 RuleHawk checking postflight rules...
✅ A1: Code Formatting - Fixed 12 formatting issues
✅ C1: Zero Warnings - Fixed 3 import warnings
❌ S1: No Hardcoded Secrets - Cannot auto-fix (manual fix required)
# Exit code: 1 (unfixable issues remain)
```

### Enforce Mode: Strict Validation Gate

Use `--enforce` when compliance is mandatory and violations should block progress:

```bash
rulehawk postflight --enforce
```

**When to use:**
- **CI/CD pipelines** as quality gate before merge
- **Production deploys** as final validation
- **Agent validation** to verify all fixes applied
- **Strict environments** where compliance is required

**What happens:**
- **Never** modifies any files
- **Reports** all violations
- **Exits 0** if no violations
- **Exits 1** if ANY violations found

**Real example:**
```bash
# CI pipeline checking PR
$ rulehawk postflight --enforce
🦅 RuleHawk checking postflight rules...
✅ A1: Code Formatting - No issues
❌ C2: Test Coverage - 75% below 80% threshold
❌ S1: No Hardcoded Secrets - API key found
# Exit code: 1 (build fails, PR blocked)
```

## Mode Selection by Role

Different roles should use different modes based on their needs:

### For Human Developers

Your typical workflow should progress through the modes:

1. **Start with check** to understand current state
2. **Use fix** to clean up automatically
3. **Use check again** to see what needs manual attention
4. **Use enforce** only when you need strict validation

```bash
# Development workflow
rulehawk preflight --check      # See what needs attention
rulehawk inflight --fix         # Fix while coding
rulehawk postflight --fix       # Clean up before commit
rulehawk postflight --check     # See what's left to fix manually
```

### For AI Agents

Agents should follow a structured workflow that uses different modes at different stages:

```
# Agent instructions
1. Start: Run `rulehawk preflight --check` to see initial state
2. During work: Run `rulehawk inflight --fix` periodically
3. Before completing: Run `rulehawk postflight --fix`
4. Verification: Run `rulehawk postflight --enforce`
5. If enforce fails: Fix issues manually, return to step 4
```

### For CI/CD Systems

Automation should use enforce mode for gates but may use fix mode for assistance:

```yaml
# GitHub Actions example
- name: Try Auto-fix
  run: rulehawk all --fix
  continue-on-error: true  # Don't fail if unfixable

- name: Enforce Quality Gate
  run: rulehawk all --enforce  # This will fail the build if issues exist
```

## Common Patterns

These patterns show typical mode usage in real scenarios:

### Pattern 1: Progressive Validation

Move from permissive to strict as code matures:

```bash
# Early development
rulehawk check  # Just see issues, don't block

# Active development
rulehawk --fix  # Start fixing automatically

# Ready for review
rulehawk --enforce  # Must pass all rules
```

### Pattern 2: Fix Then Enforce

Always try to fix before enforcing to avoid unnecessary failures:

```bash
# Good pattern
rulehawk postflight --fix     # Fix what we can
rulehawk postflight --enforce  # Verify everything fixed

# Bad pattern
rulehawk postflight --enforce  # Might fail on auto-fixable issues
```

### Pattern 3: Check Before Fix

Understand what will change before applying fixes:

```bash
# See what would be fixed
rulehawk postflight --check

# If comfortable with changes
rulehawk postflight --fix
```

## Mode Behavior Summary

This table summarizes the key behaviors of each mode:

| Behavior | Check | Fix | Enforce |
|----------|-------|-----|---------|
| **Modifies files** | Never | Yes | Never |
| **Can fail build** | Never | Only if unfixable | Yes, if any violations |
| **Shows violations** | Yes | Yes | Yes |
| **Exit code 0** | Always | If all fixed | If no violations |
| **Exit code 1** | Never | If unfixable issues | If any violations |
| **Safe for exploration** | Yes | No | Yes |
| **Use in CI/CD** | For info | With caution | Yes, as gate |
| **Use in development** | Yes | Yes | Rarely |

## Important Reminders

Key points to remember about modes:

- **Default is safe**: Without flags, RuleHawk uses check mode
- **Enforce never fixes**: It only validates, never modifies
- **Fix can fail**: Returns exit 1 if unfixable issues remain
- **Check never fails**: Always returns exit 0 for safety
- **Modes are exclusive**: Use one at a time (--check OR --fix OR --enforce)

## Troubleshooting Mode Issues

Common issues and their solutions:

### "Why didn't enforce fix my issues?"

Enforce mode never fixes anything. It's a validation gate only. Run `--fix` first, then `--enforce`.

### "Why did fix mode fail my build?"

Fix mode exits with code 1 if it encounters issues it cannot automatically fix. Check the output for what needs manual attention.

### "Why doesn't check mode fail when there are errors?"

Check mode is designed for safe exploration. It reports issues but always exits successfully. Use enforce mode if you need failures.

### "Can I combine modes?"

No, modes are mutually exclusive. Choose one based on your goal: explore (check), clean up (fix), or validate (enforce).