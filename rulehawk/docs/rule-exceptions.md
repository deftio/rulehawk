# Rule Exceptions and Skipping

RuleHawk provides flexible ways to handle rules that may not apply to your specific situation.

## The .rulehawkignore File

You can selectively disable rules using a `.rulehawkignore` file in your project root.

### Basic Format

```
# Comments start with #
RULE_ID:reason for skipping
```

### Temporary Exceptions

You can set exceptions to expire on a specific date:

```
# This rule will be re-enabled after January 31, 2024
C2:until=2024-01-31:Waiting for test framework upgrade
```

### Examples

```
# .rulehawkignore

# Development exceptions
A3:Development happens on main branch for now
P2:Task planning optional for small projects

# Temporary exceptions
S5:until=2024-02-01:pip-audit not available in CI yet

# Tool-specific exceptions
C2:Using custom test runner not compatible with pytest
```

## Verbosity Levels

Control how much detail you see in the output:

### Minimal
```bash
uv run rulehawk check --verbosity minimal
```
- Shows only rule ID, status, and brief message
- Best for CI/CD where you just need pass/fail

### Normal (default)
```bash
uv run rulehawk check --verbosity normal
```
- Shows rule name, severity, message
- First 3 error details
- Indicates if fixes are available

### Verbose
```bash
uv run rulehawk check --verbosity verbose
```
- Full rule descriptions
- Complete error details
- Command output (stdout/stderr)
- Exact fix commands
- Useful for debugging

## Output Formats

### YAML (default)
Best for both human reading and programmatic parsing:

```bash
uv run rulehawk check --output yaml
```

### JSON
For integration with other tools:

```bash
uv run rulehawk check --output json | jq '.violations[] | select(.fixable==true)'
```

### Markdown
Human-friendly report with formatting:

```bash
uv run rulehawk check --output markdown
```

## Show Skipped Rules

By default, skipped rules are hidden. To see them:

```bash
uv run rulehawk check --show-skipped
```

Output includes:
```yaml
skipped:
- rule: A3
  name: Branch Protection
  reason: Development happens on main branch for now
```

## Practical Examples

### For CI/CD
```bash
# Minimal output, fail on errors
uv run rulehawk check --verbosity minimal

# But allow specific exceptions
echo "S5:CI environment doesn't have security tools" > .rulehawkignore
```

### For Development
```bash
# Verbose output to understand issues
uv run rulehawk check --verbosity verbose --show-skipped

# Fix what can be fixed automatically
uv run rulehawk check --fix
```

### For Debugging Specific Rules
```bash
# Check just one rule with full details
uv run rulehawk check C2 --verbosity verbose --output json | jq
```

## Best Practices

1. **Document exceptions** - Always provide a clear reason
2. **Use temporary exceptions** - Set expiry dates when possible
3. **Review regularly** - Check .rulehawkignore periodically
4. **Don't over-disable** - Only skip rules that truly don't apply
5. **Different environments** - Consider different .rulehawkignore files for dev/prod

## Warning

While rule exceptions provide flexibility, use them sparingly. Each skipped rule is a potential quality gate removed. Always document why a rule doesn't apply to maintain accountability.